"""
AliağaAI — RAG (Retrieval-Augmented Generation) Sistemi.

pgvector kullanarak veritabanındaki DocumentChunk tablosunda semantik arama yapar.
"""
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding import generate_query_embedding

# DocumentChunk pgvector kurulu değilse yok sayılabilir
try:
    from app.models.city import DocumentChunk
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False


async def search_similar_chunks(session: AsyncSession, query: str, limit: int = 5, min_similarity: float = 0.85) -> list[dict]:
    """
    Kullanıcı sorusunu vektöre çevirir ve veritabanında en yakın chunk'ları bulur.
    Cosine similarity kullanır (embedding vector_cosine_ops ile indexlendiği için operatör: <=>).
    NOT: pgvector <=> operatörü `distance` döner (1 - similarity).
    Cosine similarity = 1 - (A <=> B)
    """
    if not HAS_VECTOR:
        logger.warning("RAG Araması yapılamıyor: pgvector destekli DocumentChunk yok.")
        return []

    try:
        # Sorunun vektörünü oluştur
        query_vector = await generate_query_embedding(query)
        
        # pgvector araması 
        # `embedding.cosine_distance(query_vector)` veya `<=>`
        distance_col = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
        
        stmt = (
            select(DocumentChunk, distance_col)
            # Minimum similarity filtrelemesi (distance <= 1 - min_similarity)
            .where(distance_col <= (1.0 - min_similarity))
            .order_by(distance_col)
            .limit(limit)
        )
        
        result = await session.execute(stmt)
        
        chunks = []
        for doc, distance in result:
            similarity = 1.0 - distance
            chunks.append({
                "id": str(doc.id),
                "source_type": doc.source_type,
                "content": doc.content,
                "similarity": similarity,
                "metadata": doc.metadata_json or {},
            })
            
        logger.info(f"RAG Araması: '{query}' için {len(chunks)} sonuç bulundu.")
        return chunks
        
    except Exception as e:
        logger.error(f"RAG Arama hatası: {e}")
        return []
