from __future__ import annotations

import os
from collections.abc import Iterator

from cryptography.fernet import Fernet

os.environ.setdefault("TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://coaching:coaching@localhost:5433/coaching_test"
)
os.environ.setdefault("STRAVA_CLIENT_ID", "test-strava-client")
os.environ.setdefault("STRAVA_CLIENT_SECRET", "test-strava-secret")
os.environ.setdefault("GARMIN_CLIENT_ID", "test-garmin-client")
os.environ.setdefault("GARMIN_CLIENT_SECRET", "test-garmin-secret")
os.environ.setdefault("NOLIO_CLIENT_ID", "test-nolio-client")
os.environ.setdefault("NOLIO_CLIENT_SECRET", "test-nolio-secret")

import uuid  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from src.db import SessionLocal, engine, get_db  # noqa: E402
from src.main import app  # noqa: E402
from src.models import Base  # noqa: E402
from src.models.athlete import Athlete  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _schema() -> Iterator[None]:
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db(_schema: None) -> Iterator[Session]:
    session = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def athlete(db: Session) -> Athlete:
    instance = Athlete(id=uuid.uuid4(), email="test@example.com")
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
