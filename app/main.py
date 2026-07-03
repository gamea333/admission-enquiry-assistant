from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db.seed import seed_sample_data
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_sample_data()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(router, prefix="/api")
    return app


app = create_app()
