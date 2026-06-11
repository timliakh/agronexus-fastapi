from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import engine


def upgrade_db() -> None:
    root = Path(__file__).resolve().parent.parent
    alembic_cfg = Config(str(root / "alembic.ini"))

    inspector = inspect(engine)
    has_products = inspector.has_table("products")
    has_alembic = inspector.has_table("alembic_version")

    if has_products and not has_alembic:
        command.stamp(alembic_cfg, "head")
        return

    command.upgrade(alembic_cfg, "head")
