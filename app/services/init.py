from functools import lru_cache

import httpx
from punq import Container, Scope

from app.infrastructure.asr.base import BaseASRProvider
from app.infrastructure.asr.dummy import DummyASRProvider
from app.infrastructure.asr.whisper import FasterWhisperASRProvider
from app.infrastructure.telegram.client import TelegramBotClient
from app.services.commands.transcriptions import (
    StartTranscriptionFromTelegramVoiceCommand,
    StartTranscriptionFromTelegramVoiceCommandHandler,
)
from app.services.mediator.base import Mediator
from app.settings.conf import Config


@lru_cache(1)
def init_container() -> Container:
    return _init_container()


def _init_container() -> Container:
    container = Container()

    container.register(Config, instance=Config(), scope=Scope.singleton)

    def create_http_client() -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=20)

    container.register(httpx.AsyncClient, factory=create_http_client, scope=Scope.singleton)

    def create_telegram_client() -> TelegramBotClient:
        config: Config = container.resolve(Config)
        http_client: httpx.AsyncClient = container.resolve(httpx.AsyncClient)
        return TelegramBotClient(token=config.telegram_bot_token, http_client=http_client)

    container.register(TelegramBotClient, factory=create_telegram_client, scope=Scope.singleton)

    def create_asr_provider() -> BaseASRProvider:
        config: Config = container.resolve(Config)
        if config.asr_provider.lower() == "whisper":
            return FasterWhisperASRProvider(model_name_or_path="base", compute_type="int8")
        return DummyASRProvider()

    container.register(BaseASRProvider, factory=create_asr_provider, scope=Scope.singleton)

    def init_mediator() -> Mediator:
        mediator = Mediator()
        telegram = container.resolve(TelegramBotClient)
        asr_provider = container.resolve(BaseASRProvider)
        transcription_handler = StartTranscriptionFromTelegramVoiceCommandHandler(
            telegram=telegram, asr_provider=asr_provider
        )
        mediator.register_command(StartTranscriptionFromTelegramVoiceCommand, transcription_handler)
        return mediator

    container.register(Mediator, factory=init_mediator, scope=Scope.singleton)
    return container
