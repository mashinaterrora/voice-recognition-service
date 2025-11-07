from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: Optional[str] = Field(default=None, alias="TELEGRAM_WEBHOOK_SECRET")
    admin_user_ids: List[int] = Field(default_factory=list, alias="ADMIN_USER_IDS")

    asr_provider: str = Field(default="dummy", alias="ASR_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
