from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: Optional[str] = Field(default=None, alias="TELEGRAM_WEBHOOK_SECRET")
    admin_user_ids: List[int] = Field(default_factory=list, alias="ADMIN_USER_IDS")

    asr_provider: str = Field(default="dummy", alias="ASR_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    price_per_message_stars: int = Field(default=1, alias="PRICE_PER_MESSAGE_STARS")

    update_mode: str = Field(default="webhook", alias="UPDATE_MODE")

    refund_test_mode: bool = Field(default=False, alias="REFUND_TEST_MODE")

    run_migrations_on_start: bool = Field(default=True, alias="RUN_MIGRATIONS_ON_START")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/postgres",
        alias="DATABASE_URL",
    )
