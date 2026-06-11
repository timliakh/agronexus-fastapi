from dataclasses import dataclass
from pathlib import Path

from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class DatabaseConfig:
    database_url: str


@dataclass(frozen=True)
class PathsConfig:
    base_dir: Path
    static_dir: Path
    uploads_dir: Path
    products_upload_dir: Path


@dataclass(frozen=True)
class ImageConfig:
    allowed_extensions: frozenset[str]
    max_file_size: int


@dataclass(frozen=True)
class Config:
    db: DatabaseConfig
    paths: PathsConfig
    image: ImageConfig
    secret_key: str
    admin_password: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    uploads_dir = BASE_DIR / "uploads"
    return Config(
        db=DatabaseConfig(database_url=env("DATABASE_URL")),
        paths=PathsConfig(
            base_dir=BASE_DIR,
            static_dir=BASE_DIR / "static",
            uploads_dir=uploads_dir,
            products_upload_dir=uploads_dir / "products",
        ),
        image=ImageConfig(
            allowed_extensions=frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif"}),
            max_file_size=5 * 1024 * 1024,
        ),
        secret_key=env("SECRET_KEY"),
        admin_password=env("ADMIN_PASSWORD", default="admin123"),
    )


config = load_config()
