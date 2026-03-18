from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.routes.report import router as report_router
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: pre-warm pymorphy3 analyzer (first call is slow)
    from src.infrastructure.nlp.morphology import get_normal_form

    get_normal_form("тест")

    yield

    # Shutdown: nothing to clean up for the sync path


app = FastAPI(
    title=settings.APP_TITLE,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.include_router(report_router, prefix="/public/report", tags=["report"])
