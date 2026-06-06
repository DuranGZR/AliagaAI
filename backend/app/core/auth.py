"""
AliağaAI — API Key authentication dependency.

FastAPI endpoint'lerde kullanmak için bağımlılık (dependency) sağlar.
AUTH_ENABLED=false ise kimlik doğrulaması devre dışı bırakılır.
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str | None = Security(api_key_header)) -> str | None:
    """
    API anahtarını doğrular.

    AUTH_ENABLED=false ise doğrulama yapılmaz.
    AUTH_ENABLED=true ve API_KEY ayarlanmışsa, istek başlığındaki
    X-API-Key değerinin eşleşmesi gerekir.
    """
    if not settings.AUTH_ENABLED:
        return None

    if not settings.API_KEY:
        # API anahtarı ayarlanmamışsa uyarı ver ama erişime izin ver
        from loguru import logger
        logger.warning(
            "AUTH_ENABLED=true fakat API_KEY ayarlanmamış. "
            "Lütfen .env dosyasına API_KEY ekleyin."
        )
        return None

    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key başlığı gerekli.",
        )

    if key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Geçersiz API anahtarı.",
        )

    return key


from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    """
    JWT token'ını doğrular ve veritabanından kullanıcıyı çeker.
    Bulamazsa None döner.
    """
    if not token:
        return None
    
    payload = decode_access_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        return result.scalars().first()
    except Exception:
        return None


async def get_current_active_user(
    current_user: User | None = Depends(get_current_user)
) -> User:
    """
    Aktif giriş yapmış kullanıcıyı zorunlu kılar. Giriş yapılmamışsa 401 hatası atar.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bu işlem için giriş yapılması gerekmektedir.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kullanıcı hesabı aktif değil."
        )
    return current_user

