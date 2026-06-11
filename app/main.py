from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import db_models  # noqa: F401
from app.config import config
from app.database import SessionLocal
from app.db_migrate import upgrade_db
from app.dependencies import get_image_storage
from app.exceptions import DomainError
from app.logger import logger
from app.routers import admin, feedback, meta, orders, pages, products
from app.seed import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    upgrade_db()
    get_image_storage().ensure_dir()
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="AgroNexus",
    description="Store for Autonomous Farming Technologies",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(DomainError)
async def domain_error_handler(
    _request: Request,
    error: DomainError,
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": error.message})


app.include_router(meta.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(feedback.router)
app.include_router(admin.router)

app.mount("/static", StaticFiles(directory=config.paths.static_dir), name="static")
app.mount("/uploads", StaticFiles(directory=config.paths.uploads_dir), name="uploads")

app.include_router(pages.router)
