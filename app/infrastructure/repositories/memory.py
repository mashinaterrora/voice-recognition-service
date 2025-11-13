from typing import Dict

from app.infrastructure.repositories.base import BaseUsersRepository


class InMemoryUsersRepository(BaseUsersRepository):
    def __init__(self) -> None:
        self._balances: Dict[int, int] = {}

    async def get_balance(self, user_id: int) -> int:
        return self._balances.get(user_id, 0)

    async def add_balance(self, user_id: int, stars: int) -> int:
        self._balances[user_id] = self._balances.get(user_id, 0) + max(0, stars)
        return self._balances[user_id]

    async def charge(self, user_id: int, stars: int) -> bool:
        current = self._balances.get(user_id, 0)
        if current < stars:
            return False
        self._balances[user_id] = current - stars
        return True

    async def ensure_user(self, user_id: int) -> None:
        self._balances.setdefault(user_id, 0)
