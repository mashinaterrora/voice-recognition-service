from typing import Optional

from app.infrastructure.asr.base import BaseASRProvider


class DummyASRProvider(BaseASRProvider):
    async def transcribe_from_url(self, url: str, language: Optional[str] = None) -> str:
        return "[transcription placeholder]"

    async def transcribe_from_bytes(self, data: bytes, language: Optional[str] = None) -> str:
        return "[transcription placeholder]"
