"""
AliağaAI — Embedding (Vektörleştirme) Servisi.

Metinleri 384 boyutlu vektörlere dönüştürür. 
Model: intfloat/multilingual-e5-small (veya benzeri).
"""
import asyncio
import time
from threading import Lock
from loguru import logger
from app.core.config import settings

# SentenceTransformers kütüphanesi ağır olduğu için ilk importta global olarak yüklüyoruz.
_embedding_model = None
_embedding_load_failed_at = None
_embedding_load_error = None
_embedding_model_lock = Lock()

def get_embedding_model():
    """Modeli lazy load yapar (sadece ilk çağrıldığında yükler)."""
    global _embedding_model, _embedding_load_failed_at, _embedding_load_error
    if _embedding_model is not None:
        return _embedding_model

    with _embedding_model_lock:
        if _embedding_model is not None:
            return _embedding_model
        if _embedding_load_failed_at is not None:
            elapsed = time.time() - _embedding_load_failed_at
            if elapsed < settings.EMBEDDING_RETRY_COOLDOWN_SEC:
                raise RuntimeError(
                    f"Embedding modeli son yüklemede başarısız oldu. "
                    f"Cooldown devam ediyor ({settings.EMBEDDING_RETRY_COOLDOWN_SEC - int(elapsed)}sn). "
                    f"Son hata: {_embedding_load_error}"
                )
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Embedding modeli yükleniyor: {settings.EMBEDDING_MODEL} (Bu biraz zaman alabilir)...")
            _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            _embedding_load_failed_at = None
            _embedding_load_error = None
            logger.success("Embedding modeli başarıyla yüklendi.")
        except ImportError:
            logger.error("sentence-transformers kütüphanesi bulunamadı! Lütfen pip install sentence-transformers yapın.")
            raise
        except Exception as e:
            logger.error(f"Embedding modeli yüklenirken hata: {e}")
            _embedding_load_failed_at = time.time()
            _embedding_load_error = str(e)
            raise
    return _embedding_model


async def generate_embedding(text: str, prefix: str = "passage: ") -> list[float]:
    """
    Verilen metni vektöre çevirir. Async/await uyumlu hale getirmek için 
    run_in_executor kullanır, böylece event loop engellenmez.
    """
    loop = asyncio.get_running_loop()
    model = await loop.run_in_executor(None, get_embedding_model)
    # e5 model formatı: query veya passage
    formatted_text = f"{prefix}{text.strip()}"

    # CPU bound işlem olduğu için thread pool'da çalıştırıyoruz
    vector = await loop.run_in_executor(None, lambda: model.encode(formatted_text, normalize_embeddings=True))
    
    return vector.tolist()

async def generate_query_embedding(query: str) -> list[float]:
    """Kullanıcı sorguları için vektör üretir."""
    return await generate_embedding(query, prefix="query: ")
