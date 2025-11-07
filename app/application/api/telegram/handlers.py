from fastapi import APIRouter, Depends
from punq import Container

from app.application.api.telegram.schemas import Update
from app.services.commands.transcriptions import StartTranscriptionFromTelegramVoiceCommand
from app.services.init import init_container
from app.services.mediator.base import Mediator

router = APIRouter(tags=["Telegram"])


@router.post("/webhook")
async def telegram_webhook(update: Update, container: Container = Depends(init_container)) -> dict:
    mediator: Mediator = container.resolve(Mediator)

    if update.message and update.message.voice:
        await mediator.handle_command(
            StartTranscriptionFromTelegramVoiceCommand(
                chat_id=update.message.chat.id,
                user_id=update.message.from_.id,
                file_id=update.message.voice.file_id,
            )
        )

    return {"ok": True}
