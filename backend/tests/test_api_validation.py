import hashlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @compiles(JSONB, "sqlite")
    def _compile_jsonb_sqlite(_type, compiler, **kw):
        return "JSON"

    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Tables are created on the in-memory SQLite engine above; skip the app
    # lifespan, which would run create_all against the configured Postgres URL.
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def token(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "researcher", "password": "lab123456"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_empty_dataset_sha_rejected(client, auth_headers):
    resp = client.post(
        "/api/runs",
        headers=auth_headers,
        json={
            "project": "p1",
            "name": "empty dataset",
            "dataset_content_sha256": "",
            "code_commit_sha": "abc1234",
        },
    )
    assert resp.status_code == 422
    # no run should have been created
    runs = client.get("/api/runs", headers=auth_headers).json()
    assert runs == []


def test_empty_code_sha_rejected(client, auth_headers):
    resp = client.post(
        "/api/runs",
        headers=auth_headers,
        json={
            "project": "p1",
            "name": "empty code",
            "dataset_content_sha256": _sha("ds"),
            "code_commit_sha": "",
        },
    )
    assert resp.status_code == 422
    runs = client.get("/api/runs", headers=auth_headers).json()
    assert runs == []


def test_valid_fingerprints_create_run(client, auth_headers):
    body = {
        "project": "p1",
        "name": "happy path",
        "dataset_content_sha256": _sha("ds"),
        "code_commit_sha": "abc1234",
        "description": "filled fingerprints",
    }
    resp = client.post("/api/runs", headers=auth_headers, json=body)
    assert resp.status_code == 201
    run = resp.json()
    assert run["status"] == "running"
    assert run["version"] == 1
    assert run["dataset_content_sha256"] == body["dataset_content_sha256"]
    assert run["code_commit_sha"] == body["code_commit_sha"]

    runs = client.get("/api/runs", headers=auth_headers).json()
    assert len(runs) == 1
