from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.sqlalchemy.models import Payment


class PaymentsGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_payment(self, user_id: int, stars: int, telegram_payment_charge_id: str | None) -> Payment:
        p = Payment(user_id=user_id, stars=stars, telegram_payment_id=telegram_payment_charge_id)
        self._session.add(p)
        return p

