"""
Kullanıcı Pydantic Şemaları.
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Şifre en az 6 karakter olmalıdır.")
    full_name: str = Field(..., min_length=2, description="Ad soyad en az 2 karakter olmalıdır.")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str
    email: EmailStr | None = None
    full_name: str | None = None
    avatar_url: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    avatar_url: str | None = None
    is_google_user: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
