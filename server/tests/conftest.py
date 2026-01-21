import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.db.models import Base
from app.settings import settings as app_settings


@pytest.fixture()
def client(tmp_path):
    db_file = tmp_path / "test.db"
    app_settings.db_dsn = f"sqlite+pysqlite:///{db_file}"

    engine = create_engine(app_settings.db_dsn, future=True)
    Base.metadata.create_all(bind=engine)

    app = create_app()

    published = {"order_ids": []}

    async def fake_publisher(order_id: int):
        published["order_ids"].append(order_id)

    app.state.publisher = fake_publisher
    app.state.published = published

    with TestClient(app) as c:
        yield c
