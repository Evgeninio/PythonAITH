from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session


def create_engine_and_sessionmaker(dsn: str) -> tuple[Engine, sessionmaker]:
    engine = create_engine(dsn, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine, SessionLocal


def get_db(request) -> Session:
    return request.state.db
