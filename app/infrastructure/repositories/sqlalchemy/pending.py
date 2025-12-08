from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.sqlalchemy.models import PendingTranscription


class PendingTranscriptionsGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user_id: int, chat_id: int, message_id: int, file_id: str) -> PendingTranscription:
        pending = PendingTranscription(user_id=user_id, chat_id=chat_id, message_id=message_id, file_id=file_id)
        self._session.add(pending)
        return pending

    async def get_next_for_user(self, user_id: int) -> Optional[PendingTranscription]:
        res = await self._session.execute(
            select(PendingTranscription).where(PendingTranscription.user_id == user_id).order_by(PendingTranscription.created_at.asc()).limit(1)
        )
        return res.scalar_one_or_none()

    async def remove(self, pending: PendingTranscription) -> None:
        await self._session.delete(pending)

