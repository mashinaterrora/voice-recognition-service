from fastapi import FastAPI

from app.application.api.lifespan import lifespan
from app.application.api.telegram.handlers import router as telegram_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Voice Recognition Service",
        docs_url="/api/docs",
        description="Telegram voice to text service (DDD/CQRS)",
        debug=True,
        lifespan=lifespan,
    )

    app.include_router(telegram_router, prefix="/telegram")
    return app
