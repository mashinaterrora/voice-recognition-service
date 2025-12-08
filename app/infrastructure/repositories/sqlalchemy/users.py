from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.sqlalchemy.models import User


class UsersGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        res = await self._session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    async def ensure_user(self, user_id: int) -> User:
        user = await self.get_by_id(user_id)
        if user is None:
            user = User(id=user_id, balance_stars=0)
            self._session.add(user)
        return user

    async def get_balance(self, user_id: int) -> int:
        user = await self.get_by_id(user_id)
        return user.balance_stars if user else 0

    async def add_balance(self, user_id: int, stars: int) -> int:
        user = await self.ensure_user(user_id)
        user.balance_stars = int(user.balance_stars) + max(0, int(stars))
        return user.balance_stars

    async def charge(self, user_id: int, stars: int) -> bool:
        user = await self.ensure_user(user_id)
        if user.balance_stars < stars:
            return False
        user.balance_stars = user.balance_stars - int(stars)
        return True

    async def add(self, model: User) -> None:
        self._session.add(model)

    async def update(self, model: User) -> None:
        pass

    async def remove(self, model: User) -> None:
        await self._session.delete(model)

