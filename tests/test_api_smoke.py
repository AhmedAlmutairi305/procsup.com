import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from app.main import app


def test_health_and_list_runs():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/api/runs").status_code == 200
