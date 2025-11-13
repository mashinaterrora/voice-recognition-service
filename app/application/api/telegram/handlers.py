import logging
from fastapi import APIRouter, Depends
from punq import Container

from app.application.api.telegram.schemas import Update
from app.infrastructure.persistence.sqlalchemy.models import PendingTranscription, Payment
from app.infrastructure.repositories.sqlalchemy.pending import PendingTranscriptionsGateway
from app.infrastructure.repositories.sqlalchemy.payments import PaymentsGateway
from app.infrastructure.telegram.client import TelegramBotClient
from app.services.billing import BillingService
from app.services.commands.transcriptions import StartTranscriptionFromTelegramVoiceCommand
from app.services.init import init_container
from app.services.mediator.base import Mediator
from app.services.uow.sqlalchemy import SQLAlchemyUnitOfWork
from app.settings.conf import Config

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Telegram"])


@router.post("/webhook")
async def telegram_webhook(update: Update, container: Container = Depends(init_container)) -> dict:
    logger.debug("update received: %s", update.dict(exclude_none=True))
    mediator: Mediator = container.resolve(Mediator)
    billing: BillingService = container.resolve(BillingService)
    telegram: TelegramBotClient = container.resolve(TelegramBotClient)
    config: Config = container.resolve(Config)
    uow_factory = lambda: container.resolve(SQLAlchemyUnitOfWork)

    if update.pre_checkout_query:
        try:
            await telegram.answer_pre_checkout_query(pre_checkout_query_id=update.pre_checkout_query.id, ok=True)
        except Exception as e:
            logger.exception("answer_pre_checkout_query failed: %s", e)
        return {"ok": True}

    if update.message and update.message.successful_payment:
        sp = update.message.successful_payment
        async with uow_factory().transaction() as uow:
            payments: PaymentsGateway = uow.repository(Payment)
            await payments.add_payment(
                user_id=update.message.from_.id,
                stars=sp.total_amount,
                telegram_payment_charge_id=sp.telegram_payment_charge_id,
            )

        if config.refund_test_mode:
            if sp.telegram_payment_charge_id:
                try:
                    await telegram.refund_star_payment(
                        user_id=update.message.from_.id,
                        telegram_payment_charge_id=sp.telegram_payment_charge_id,
                    )
                except Exception as e:
                    logger.exception("refund_star_payment failed: %s", e)
            async with uow_factory().transaction() as uow:
                pending_gateway: PendingTranscriptionsGateway = uow.repository(PendingTranscription)
                pending = await pending_gateway.get_next_for_user(update.message.from_.id)
                if pending:
                    try:
                        await mediator.handle_command(
                            StartTranscriptionFromTelegramVoiceCommand(
                                chat_id=pending.chat_id,
                                user_id=update.message.from_.id,
                                file_id=pending.file_id,
                                message_id=pending.message_id,
                            )
                        )
                    except Exception as e:
                        logger.exception("transcription after payment failed: %s", e)
                    await pending_gateway.remove(pending)
            return {"ok": True}

        await billing.credit_on_successful_payment(user_id=update.message.from_.id, stars=sp.total_amount)
        async with uow_factory().transaction() as uow:
            pending_gateway: PendingTranscriptionsGateway = uow.repository(PendingTranscription)
            pending = await pending_gateway.get_next_for_user(update.message.from_.id)
            if pending:
                try:
                    await mediator.handle_command(
                        StartTranscriptionFromTelegramVoiceCommand(
                            chat_id=pending.chat_id,
                            user_id=update.message.from_.id,
                            file_id=pending.file_id,
                            message_id=pending.message_id,
                        )
                    )
                except Exception as e:
                    logger.exception("transcription after payment failed: %s", e)
                await pending_gateway.remove(pending)
        return {"ok": True}

    if update.message and update.message.voice:
        billing_result = await billing.ensure_credit_or_notify(
            chat_id=update.message.chat.id, user_id=update.message.from_.id
        )
        if not billing_result.allowed:
            async with uow_factory().transaction() as uow:
                pending_gateway: PendingTranscriptionsGateway = uow.repository(PendingTranscription)
                await pending_gateway.add(
                    user_id=update.message.from_.id,
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                    file_id=update.message.voice.file_id,
                )
            try:
                await telegram.send_invoice(
                    chat_id=update.message.chat.id,
                    title="Top up Stars",
                    description=(
                        "Voice recognition payment\n\n"
                        "Insufficient stars. Please complete the payment and I will transcribe this message."
                    ),
                    payload="topup_one_message",
                    currency="XTR",
                    prices=[{"label": "Stars", "amount":  billing._config.price_per_message_stars}],
                    reply_to_message_id=update.message.message_id,
                )
            except Exception as e:
                logger.exception("sending invoice failed: %s", e)
            return {"ok": True}
        try:
            await mediator.handle_command(
                StartTranscriptionFromTelegramVoiceCommand(
                    chat_id=update.message.chat.id,
                    user_id=update.message.from_.id,
                    file_id=update.message.voice.file_id,
                    message_id=update.message.message_id,
                )
            )
        except Exception as e:
            logger.exception("transcription failed: %s", e)

    return {"ok": True}
