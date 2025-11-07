from dataclasses import dataclass
from typing import Optional

import httpx

from app.infrastructure.asr.base import BaseASRProvider
from app.settings.conf import Config


@dataclass
class StartTranscriptionFromTelegramVoiceCommand:
    chat_id: int
    user_id: int
    file_id: str
    language: Optional[str] = None


class StartTranscriptionFromTelegramVoiceCommandHandler:
    def __init__(self, config: Config, http_client: httpx.AsyncClient, asr_provider: BaseASRProvider) -> None:
        self._config = config
        self._http = http_client
        self._asr = asr_provider

    async def __call__(self, cmd: StartTranscriptionFromTelegramVoiceCommand) -> str:
        return await self._asr.transcribe_from_url(url="telegram:file")
