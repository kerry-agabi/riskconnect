"""Shared test fixtures for the RiskLens backend."""

from __future__ import annotations

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from risklens_api.api.deps import get_submission_service
from risklens_api.core.config import Settings
from risklens_api.main import app
from risklens_api.services.fakes import FakeQueueService, FakeStorageService
from risklens_api.services.submission_service import SubmissionService


@pytest.fixture()
def settings() -> Settings:
    return Settings()


@pytest.fixture()
def fake_storage() -> FakeStorageService:
    return FakeStorageService()


@pytest.fixture()
def fake_queue() -> FakeQueueService:
    return FakeQueueService()


@pytest.fixture()
def submission_service(
    settings: Settings,
    fake_storage: FakeStorageService,
    fake_queue: FakeQueueService,
) -> SubmissionService:
    return SubmissionService(
        settings=settings,
        storage=fake_storage,
        queue=fake_queue,
        id_generator=lambda: "TEST-ID-001",
    )


@pytest.fixture()
def client(submission_service: SubmissionService) -> Generator[TestClient, None, None]:
    """TestClient with fake services injected."""
    app.dependency_overrides[get_submission_service] = lambda: submission_service
    yield TestClient(app)
    app.dependency_overrides.clear()
