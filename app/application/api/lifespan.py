import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from app.services.init import init_container
from app.settings.conf import Config
from app.services.polling import run_polling


@asynccontextmanager
async def lifespan(*_):
    container = init_container()
    config: Config = container.resolve(Config)

    polling_task: Optional[asyncio.Task] = None
    try:
        if config.update_mode.lower() == "polling":
            polling_task = asyncio.create_task(run_polling(container))
        yield
    finally:
        if polling_task:
            polling_task.cancel()
            try:
                await polling_task
            except Exception:
                pass
