"""FastAPI dependency injection for services."""

from __future__ import annotations

from risklens_api.core.config import get_settings
from risklens_api.services.fakes import FakeQueueService, FakeStorageService
from risklens_api.services.submission_service import SubmissionService

_storage = FakeStorageService()
_queue = FakeQueueService()
_service: SubmissionService | None = None


def get_submission_service() -> SubmissionService:
    """Return a singleton SubmissionService. Override in tests via app.dependency_overrides."""
    global _service  # noqa: PLW0603
    if _service is None:
        _service = SubmissionService(
            settings=get_settings(),
            storage=_storage,
            queue=_queue,
        )
    return _service
