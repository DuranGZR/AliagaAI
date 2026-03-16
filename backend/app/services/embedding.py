import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded")
    return _model


class EmbeddingService:
    @staticmethod
    def encode(text: str) -> list[float]:
        model = _get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    @staticmethod
    def encode_batch(texts: list[str]) -> list[list[float]]:
        model = _get_model()
        embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()

    @staticmethod
    def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
        chunk_size = chunk_size or settings.rag_chunk_size
        overlap = overlap or settings.rag_chunk_overlap

        if len(text) <= chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            if end < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                split_at = max(last_period, last_newline)
                if split_at > chunk_size * 0.3:
                    chunk = chunk[: split_at + 1]
                    end = start + split_at + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return [c for c in chunks if c]
