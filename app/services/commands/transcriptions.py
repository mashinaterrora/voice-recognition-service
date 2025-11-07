from dataclasses import dataclass
from typing import Optional

from app.infrastructure.asr.base import BaseASRProvider
from app.infrastructure.telegram.client import TelegramBotClient


@dataclass
class StartTranscriptionFromTelegramVoiceCommand:
    chat_id: int
    user_id: int
    file_id: str
    language: Optional[str] = None


class StartTranscriptionFromTelegramVoiceCommandHandler:
    def __init__(self, telegram: TelegramBotClient, asr_provider: BaseASRProvider) -> None:
        self._telegram = telegram
        self._asr = asr_provider

    async def __call__(self, cmd: StartTranscriptionFromTelegramVoiceCommand) -> str:
        file_path = await self._telegram.get_file_path(cmd.file_id)
        audio_bytes = await self._telegram.download_file(file_path)
        text = await self._asr.transcribe_from_bytes(audio_bytes, language=cmd.language)
        if text:
            await self._telegram.send_message(chat_id=cmd.chat_id, text=text)
        else:
            await self._telegram.send_message(chat_id=cmd.chat_id, text="Не удалось распознать голосовое сообщение.")
        return text
