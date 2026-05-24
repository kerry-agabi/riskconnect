"""Core business service for submission lifecycle management."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Protocol

from risklens_api.core.config import Settings
from risklens_api.core.constants import ALLOWED_CONTENT_TYPES, SubmissionStatus
from risklens_api.core.errors import (
    FileTooLargeError,
    InvalidContentTypeError,
    SubmissionNotFoundError,
    SummaryNotAvailableError,
)
from risklens_api.core.logging import get_logger
from risklens_api.schemas.submissions import (
    FileInfo,
    ProgressInfo,
    StartProcessingResponse,
    SubmissionListItem,
    SubmissionListResponse,
    SubmissionStatusResponse,
    SummaryResponse,
    UploadUrlResponse,
)


class StorageService(Protocol):
    """Protocol for presigned URL generation (S3 or fake)."""

    def generate_presigned_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        expires_in: int,
    ) -> str: ...


class QueueService(Protocol):
    """Protocol for processing queue (SQS or fake)."""

    def send_processing_message(self, submission_id: str, object_key: str) -> None: ...


class SubmissionRecord:
    """Internal mutable record for a submission."""

    def __init__(
        self,
        submission_id: str,
        file_name: str,
        content_type: str,
        object_key: str,
        file_size_bytes: int,
    ) -> None:
        self.submission_id = submission_id
        self.file_name = file_name
        self.content_type = content_type
        self.object_key = object_key
        self.file_size_bytes = file_size_bytes
        self.status = SubmissionStatus.UPLOADED
        now = datetime.now(timezone.utc)
        self.created_at = now
        self.updated_at = now
        self.progress: ProgressInfo | None = None
        self.error: str | None = None


class SubmissionService:
    """Orchestrates submission creation, status queries, and processing triggers."""

    def __init__(
        self,
        settings: Settings,
        storage: StorageService,
        queue: QueueService,
        id_generator: Callable[[], str] | None = None,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._queue = queue
        if id_generator is None:
            from risklens_api.core.ids import generate_id

            id_generator = generate_id
        self._generate_id = id_generator
        self._submissions: dict[str, SubmissionRecord] = {}
        self._logger = get_logger()

    def create_upload_url(
        self,
        file_name: str,
        content_type: str,
        file_size_bytes: int,
    ) -> UploadUrlResponse:
        """Validate inputs, create a record, and return a presigned upload URL."""
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidContentTypeError(content_type)
        if file_size_bytes > self._settings.max_file_size_bytes:
            raise FileTooLargeError(file_size_bytes, self._settings.max_file_size_bytes)

        submission_id = self._generate_id()
        object_key = f"submissions/{submission_id}/raw/{file_name}"

        upload_url = self._storage.generate_presigned_upload_url(
            bucket=self._settings.s3_bucket,
            key=object_key,
            content_type=content_type,
            expires_in=self._settings.upload_expiry_seconds,
        )

        record = SubmissionRecord(
            submission_id=submission_id,
            file_name=file_name,
            content_type=content_type,
            object_key=object_key,
            file_size_bytes=file_size_bytes,
        )
        self._submissions[submission_id] = record

        self._logger.info(
            "Upload URL created",
            extra={"submission_id": submission_id, "status": record.status},
        )

        return UploadUrlResponse(
            submission_id=submission_id,
            upload_url=upload_url,
            object_key=object_key,
            expires_in_seconds=self._settings.upload_expiry_seconds,
            max_file_size_bytes=self._settings.max_file_size_bytes,
        )

    def start_processing(
        self, submission_id: str, object_key: str
    ) -> StartProcessingResponse:
        """Queue a submission for async processing. Idempotent: re-starting an
        already-queued (or further-progressed) submission returns current status
        without re-queuing."""
        record = self._submissions.get(submission_id)
        if record is None:
            raise SubmissionNotFoundError(submission_id)

        # Idempotent: only queue if still in UPLOADED state
        if record.status == SubmissionStatus.UPLOADED:
            self._queue.send_processing_message(submission_id, object_key)
            record.status = SubmissionStatus.QUEUED
            record.updated_at = datetime.now(timezone.utc)

            self._logger.info(
                "Processing started",
                extra={"submission_id": submission_id, "status": record.status},
            )
        else:
            self._logger.info(
                "Start processing called but submission already past UPLOADED",
                extra={"submission_id": submission_id, "status": record.status},
            )

        return StartProcessingResponse(
            submission_id=submission_id,
            status=record.status,
        )

    def get_status(self, submission_id: str) -> SubmissionStatusResponse:
        """Return current status and metadata for a submission."""
        record = self._submissions.get(submission_id)
        if record is None:
            raise SubmissionNotFoundError(submission_id)

        return SubmissionStatusResponse(
            submission_id=record.submission_id,
            status=record.status,
            created_at=record.created_at,
            updated_at=record.updated_at,
            progress=record.progress,
            file=FileInfo(
                file_name=record.file_name,
                content_type=record.content_type,
            ),
            error=record.error,
        )

    def get_summary(self, submission_id: str) -> SummaryResponse:
        """Return summary data. Only available when status is READY or NEEDS_REVIEW."""
        record = self._submissions.get(submission_id)
        if record is None:
            raise SubmissionNotFoundError(submission_id)
        if record.status not in (SubmissionStatus.READY, SubmissionStatus.NEEDS_REVIEW):
            raise SummaryNotAvailableError(submission_id, record.status)

        return SummaryResponse(
            submission_id=record.submission_id,
            status=record.status,
            extracted=None,
            hazards=None,
        )

    def list_submissions(
        self,
        status: SubmissionStatus | None = None,
        limit: int = 25,
        next_token: str | None = None,
    ) -> SubmissionListResponse:
        """List submissions, optionally filtered by status.
        Pagination uses the last submission_id as cursor (next_token)."""
        records = list(self._submissions.values())
        if status is not None:
            records = [r for r in records if r.status == status]
        records.sort(key=lambda r: r.created_at, reverse=True)

        # Apply cursor-based pagination: skip records until we pass the cursor
        if next_token is not None:
            found = False
            filtered: list[SubmissionRecord] = []
            for r in records:
                if found:
                    filtered.append(r)
                elif r.submission_id == next_token:
                    found = True
            records = filtered

        page = records[:limit]
        items = [
            SubmissionListItem(
                submission_id=r.submission_id,
                status=r.status,
                created_at=r.created_at,
                file_name=r.file_name,
            )
            for r in page
        ]

        # If there are more records beyond this page, provide a next_token
        result_next_token: str | None = None
        if len(records) > limit:
            result_next_token = page[-1].submission_id

        return SubmissionListResponse(items=items, next_token=result_next_token)
