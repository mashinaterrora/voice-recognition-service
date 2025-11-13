from dataclasses import dataclass
from typing import Callable

from app.infrastructure.persistence.sqlalchemy.models import User
from app.infrastructure.repositories.sqlalchemy.users import UsersGateway
from app.infrastructure.telegram.client import TelegramBotClient
from app.services.uow.sqlalchemy import SQLAlchemyUnitOfWork
from app.settings.conf import Config


@dataclass
class BillingResult:
    allowed: bool
    message: str | None = None


class BillingService:
    def __init__(
        self,
        config: Config,
        uow_factory: Callable[[], SQLAlchemyUnitOfWork],
        telegram: TelegramBotClient,
    ) -> None:
        self._config = config
        self._uow_factory = uow_factory
        self._telegram = telegram

    def is_admin(self, user_id: int) -> bool:
        return user_id in self._config.admin_user_ids

    async def ensure_credit_or_notify(self, chat_id: int, user_id: int) -> BillingResult:
        if self.is_admin(user_id):
            return BillingResult(allowed=True)

        async with self._uow_factory().transaction() as uow:
            users: UsersGateway = uow.repository(User)
            await users.ensure_user(user_id)
            balance = await users.get_balance(user_id)
            price = self._config.price_per_message_stars
            if balance >= price:
                charged = await users.charge(user_id, price)
                if charged:
                    return BillingResult(allowed=True)

        return BillingResult(allowed=False, message="Insufficient stars")

    async def credit_on_successful_payment(self, user_id: int, stars: int) -> int:
        async with self._uow_factory().transaction() as uow:
            users: UsersGateway = uow.repository(User)
            await users.ensure_user(user_id)
            return await users.add_balance(user_id, stars)
