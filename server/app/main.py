from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import text

from app.settings import settings
from app.db.session import create_engine_and_sessionmaker
from app.db.models import Base
from app.api.orders import router as orders_router
from app.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SECONDS


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine, SessionLocal = create_engine_and_sessionmaker(settings.db_dsn)
        Base.metadata.create_all(bind=engine)

        app.state.engine = engine
        app.state.SessionLocal = SessionLocal

        yield
        engine.dispose()

    app = FastAPI(title="Mini Order System", lifespan=lifespan)

    @app.middleware("http")
    async def db_and_metrics_middleware(request: Request, call_next):
        started = time.time()
        request.state.db = request.app.state.SessionLocal()

        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            elapsed = time.time() - started
            path = request.url.path
            method = request.method

            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(elapsed)
            HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=str(status_code)).inc()

            request.state.db.close()

    @app.get("/health")
    async def health(request: Request):
        db = request.state.db
        db.execute(text("SELECT 1"))
        return {"status": "ok"}

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(orders_router)

    return app


app = create_app()
