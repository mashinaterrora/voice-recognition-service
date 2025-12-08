import asyncio
import os
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig


def _make_alembic_config(database_url: str) -> AlembicConfig:
    project_root = Path(__file__).resolve().parent.parent.parent
    cfg_path = project_root / "alembic.ini"
    cfg = AlembicConfig(str(cfg_path))
    cfg.set_main_option("sqlalchemy.url", database_url)
    return cfg


async def run_migrations(database_url: str) -> None:
    cfg = _make_alembic_config(database_url)
    await asyncio.to_thread(command.upgrade, cfg, "head")

