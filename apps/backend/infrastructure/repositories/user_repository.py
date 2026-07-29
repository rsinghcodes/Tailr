import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.user.models import User
from domain.user.repository import UserRepository
from infrastructure.database.user_models import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
        return self._to_domain(db_user)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
        return self._to_domain(db_user)

    async def create(self, user: User) -> User:
        db_user = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
        )
        self.session.add(db_user)
        await self.session.flush()
        await self.session.commit()
        return self._to_domain(db_user)

    def _to_domain(self, db_user: UserModel) -> User:
        return User(
            id=db_user.id,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            full_name=db_user.full_name,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
