"""
Güvenlik yardımcı işlevleri (bcrypt ve JWT).
"""
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from app.core.config import settings


def hash_password(password: str) -> str:
    """Şifreyi bcrypt kullanarak hash'ler."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Düz metin şifreyi hash'lenmiş şifreyle doğrular."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT Access Token oluşturur."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """JWT Access Token'ı doğrular ve çözer."""
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        exp = decoded_token.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None
        return decoded_token
    except jwt.PyJWTError:
        return None
