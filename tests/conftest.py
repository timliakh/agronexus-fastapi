import os
import subprocess
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ADMIN_PASSWORD"] = "test-admin-pass"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import Base, engine
from app.main import app

ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
ROOT = Path(__file__).resolve().parent.parent
SPA_INDEX = ROOT / "static" / "dist" / "index.html"


def _ensure_frontend_built() -> None:
    if SPA_INDEX.is_file():
        return
    frontend = ROOT / "frontend"
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    subprocess.run([npm, "install"], cwd=frontend, check=True)
    subprocess.run([npm, "run", "build"], cwd=frontend, check=True)


@pytest.fixture(scope="session", autouse=True)
def build_frontend_once():
    _ensure_frontend_built()


def _reset_database() -> None:
    with engine.begin() as conn:
        Base.metadata.drop_all(bind=conn)
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))


@pytest.fixture
def client():
    _reset_database()
    with TestClient(app) as test_client:
        yield test_client
    _reset_database()


@pytest.fixture
def admin_token(client: TestClient) -> str:
    response = client.post("/admin/api/login", json={"password": ADMIN_PASSWORD})
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"X-Admin-Token": admin_token}
