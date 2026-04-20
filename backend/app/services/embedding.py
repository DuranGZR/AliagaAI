"""
AliağaAI — Embedding (Vektörleştirme) Servisi.

Metinleri 384 boyutlu vektörlere dönüştürür. 
Model: intfloat/multilingual-e5-small (veya benzeri).
"""
import asyncio
from loguru import logger
from app.core.config import settings

# SentenceTransformers kütüphanesi ağır olduğu için ilk importta global olarak yüklüyoruz.
_embedding_model = None

def get_embedding_model():
    """Modeli lazy load yapar (sadece ilk çağrıldığında yükler)."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Embedding modeli yükleniyor: {settings.EMBEDDING_MODEL} (Bu biraz zaman alabilir)...")
            # e5 modelleri sorgularda "query: ", dokümanlarda "passage: " prefix'i önerir.
            # Şimdilik standart kullanım.
            _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.success("Embedding modeli başarıyla yüklendi.")
        except ImportError:
            logger.error("sentence-transformers kütüphanesi bulunamadı! Lütfen pip install sentence-transformers yapın.")
            raise
        except Exception as e:
            logger.error(f"Embedding modeli yüklenirken hata: {e}")
            raise
    return _embedding_model


async def generate_embedding(text: str, prefix: str = "passage: ") -> list[float]:
    """
    Verilen metni vektöre çevirir. Async/await uyumlu hale getirmek için 
    run_in_executor kullanır, böylece event loop engellenmez.
    """
    model = get_embedding_model()
    # e5 model formatı: query veya passage
    formatted_text = f"{prefix}{text.strip()}"
    
    loop = asyncio.get_running_loop()
    # CPU bound işlem olduğu için thread pool'da çalıştırıyoruz
    vector = await loop.run_in_executor(None, lambda: model.encode(formatted_text, normalize_embeddings=True))
    
    return vector.tolist()

async def generate_query_embedding(query: str) -> list[float]:
    """Kullanıcı sorguları için vektör üretir."""
    return await generate_embedding(query, prefix="query: ")
