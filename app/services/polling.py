import asyncio
import logging
from typing import Optional

from punq import Container

from app.application.api.telegram.schemas import Update
from app.infrastructure.persistence.sqlalchemy.models import PendingTranscription, Payment
from app.infrastructure.repositories.sqlalchemy.pending import PendingTranscriptionsGateway
from app.infrastructure.repositories.sqlalchemy.payments import PaymentsGateway
from app.infrastructure.telegram.client import TelegramBotClient
from app.services.billing import BillingService
from app.services.commands.transcriptions import StartTranscriptionFromTelegramVoiceCommand
from app.services.mediator.base import Mediator
from app.services.uow.sqlalchemy import SQLAlchemyUnitOfWork
from app.settings.conf import Config

logger = logging.getLogger(__name__)


async def run_polling(container: Container) -> None:
    telegram: TelegramBotClient = container.resolve(TelegramBotClient)
    mediator: Mediator = container.resolve(Mediator)
    billing: BillingService = container.resolve(BillingService)
    config: Config = container.resolve(Config)
    uow_factory = lambda: container.resolve(SQLAlchemyUnitOfWork)

    try:
        await telegram.delete_webhook()
        logger.debug("webhook deleted; start polling")
    except Exception as e:
        logger.debug("failed to delete webhook: %s", e)

    offset: Optional[int] = None
    while True:
        try:
            updates = await telegram.get_updates(offset=offset, timeout=30)
            for raw in updates:
                offset = raw.get("update_id", 0) + 1
                update = Update(**raw)
                logger.debug("polled update: %s", update.dict(exclude_none=True))

                if update.pre_checkout_query:
                    try:
                        await telegram.answer_pre_checkout_query(pre_checkout_query_id=update.pre_checkout_query.id, ok=True)
                    except Exception as e:
                        logger.exception("answer_pre_checkout_query failed: %s", e)
                    continue

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
                        continue

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
                    continue

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
                        continue

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
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception("polling loop error: %s", e)
            await asyncio.sleep(2)
