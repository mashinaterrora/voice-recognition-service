from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings.conf import Config


def create_engine(config: Config) -> AsyncEngine:
    return create_async_engine(config.database_url, echo=False, future=True)


def create_session_factory(engine: AsyncEngine):
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

