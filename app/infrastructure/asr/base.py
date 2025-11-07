from abc import ABC, abstractmethod
from typing import Optional


class BaseASRProvider(ABC):
    @abstractmethod
    async def transcribe_from_url(self, url: str, language: Optional[str] = None) -> str:
        raise NotImplementedError

    @abstractmethod
    async def transcribe_from_bytes(self, data: bytes, language: Optional[str] = None) -> str:
        raise NotImplementedError
