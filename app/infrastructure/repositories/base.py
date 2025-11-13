from abc import ABC, abstractmethod
from typing import Optional


class BaseUsersRepository(ABC):
    @abstractmethod
    async def get_balance(self, user_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    async def add_balance(self, user_id: int, stars: int) -> int:
        raise NotImplementedError

    @abstractmethod
    async def charge(self, user_id: int, stars: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def ensure_user(self, user_id: int) -> None:
        raise NotImplementedError
