import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from config.settings import settings
from domain.user.models import User, UserCreate, UserResponse, TokenResponse
from domain.user.repository import UserRepository


def _prehash(password: str) -> bytes:
    return hashlib.sha256(password.encode()).digest()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(_prehash(password), hashed.encode())


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, data: UserCreate) -> TokenResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        user = User(
            id=uuid.uuid4(),
            email=data.email,
            hashed_password=_hash_password(data.password),
            full_name=data.full_name,
        )
        created = await self.user_repo.create(user)
        token = self._create_token(created.id)
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=created.id,
                email=created.email,
                full_name=created.full_name,
                created_at=created.created_at,
            ),
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        if not _verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")
        token = self._create_token(user.id)
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
            ),
        )

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    def _create_token(self, user_id: uuid.UUID) -> str:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "exp": expires,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def verify_token(token: str) -> Optional[uuid.UUID]:
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            user_id_str = payload.get("sub")
            if user_id_str is None:
                return None
            return uuid.UUID(user_id_str)
        except (JWTError, ValueError):
            return None
