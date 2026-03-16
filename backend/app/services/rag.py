from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pgvector.sqlalchemy import Vector

from app.models import DocumentChunk
from app.services.embedding import EmbeddingService
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._embedding = EmbeddingService()

    async def search_similar(
        self,
        query: str,
        top_k: int | None = None,
        source_table: str | None = None,
    ) -> list[dict]:
        top_k = top_k or settings.rag_top_k
        query_embedding = self._embedding.encode(query)

        stmt = (
            select(
                DocumentChunk.id,
                DocumentChunk.content,
                DocumentChunk.source_table,
                DocumentChunk.source_id,
                DocumentChunk.metadata_,
                DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .order_by("distance")
            .limit(top_k)
        )

        if source_table:
            stmt = stmt.where(DocumentChunk.source_table == source_table)

        result = await self._db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": row.id,
                "content": row.content,
                "source_table": row.source_table,
                "source_id": row.source_id,
                "metadata": row.metadata_,
                "similarity": 1 - row.distance,
            }
            for row in rows
            if (1 - row.distance) >= settings.rag_similarity_threshold
        ]

    async def ingest_document(
        self,
        source_table: str,
        source_id: int,
        content: str,
        metadata: dict | None = None,
    ) -> int:
        chunks = self._embedding.chunk_text(content)
        embeddings = self._embedding.encode_batch(chunks)

        count = 0
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            doc_chunk = DocumentChunk(
                source_table=source_table,
                source_id=source_id,
                chunk_index=i,
                content=chunk,
                embedding=emb,
                metadata_=metadata or {},
            )
            self._db.add(doc_chunk)
            count += 1

        await self._db.flush()
        return count

    async def delete_document_chunks(self, source_table: str, source_id: int) -> int:
        result = await self._db.execute(
            text(
                "DELETE FROM document_chunks WHERE source_table = :table AND source_id = :id"
            ),
            {"table": source_table, "id": source_id},
        )
        return result.rowcount
