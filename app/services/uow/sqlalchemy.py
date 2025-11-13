from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.uow.base import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def commit(self) -> None:
        await super().commit()
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    @asynccontextmanager
    async def transaction(self):
        try:
            yield self
            await self.commit()
        except Exception as exc:
            await self.rollback()
            raise exc
