"""
Fixtures bersama buat semua test.

Test DB: pakai Postgres yang sama dengan lokal (docker-compose), tapi database
terpisah ("my_itineraries_test") supaya gak nyampur sama data dev. Tabel dibuat
lewat Base.metadata.create_all() khusus di test (bukan Alembic) -- cukup buat
kebutuhan test, gak perlu riwayat migration di sini.
"""
import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/my_itineraries_test",
)
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("GEMINI_API_KEY", "test-fake-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.database import get_db

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    """Kosongkan semua tabel sebelum tiap test, biar test satu sama lain tidak saling ganggu."""
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register + login user baru, kembalikan header Authorization siap pakai."""
    email = "tester@example.com"
    client.post(
        "/auth/register",
        json={"name": "Tester", "email": email, "password": "secret123"},
    )
    resp = client.post("/auth/login", json={"email": email, "password": "secret123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
