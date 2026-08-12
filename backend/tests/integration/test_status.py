"""Integration tests for GET /status (FR-006, SC-002)."""

import os
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from app import app

BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:7777")


@pytest.fixture
def in_process_client() -> TestClient:
    return TestClient(app)


def test_status_in_process_returns_200_json_within_2s(
    in_process_client: TestClient,
) -> None:
    start = time.monotonic()
    response = in_process_client.get("/status")
    elapsed = time.monotonic() - start

    assert response.status_code == 200
    response.json()
    assert elapsed < 2.0


@pytest.mark.integration
def test_status_live_backend_returns_200_json_within_2s() -> None:
    """Hits BACKEND_BASE_URL when backend is running (make dev-backend)."""
    start = time.monotonic()
    with httpx.Client(timeout=5.0) as client:
        response = client.get(f"{BACKEND_BASE_URL}/status")
    elapsed = time.monotonic() - start

    assert response.status_code == 200
    response.json()
    assert elapsed < 2.0
