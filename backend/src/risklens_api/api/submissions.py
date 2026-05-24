"""Submission API route handlers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from risklens_api.api.deps import get_submission_service
from risklens_api.core.constants import MAX_LIST_LIMIT, SubmissionStatus
from risklens_api.core.errors import (
    FileTooLargeError,
    InvalidContentTypeError,
    SubmissionNotFoundError,
    SummaryNotAvailableError,
)
from risklens_api.schemas.submissions import (
    StartProcessingRequest,
    StartProcessingResponse,
    SubmissionListResponse,
    SubmissionStatusResponse,
    SummaryResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from risklens_api.services.submission_service import SubmissionService

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post("/upload-url", response_model=UploadUrlResponse, status_code=201)
def create_upload_url(
    body: UploadUrlRequest,
    service: SubmissionService = Depends(get_submission_service),
) -> UploadUrlResponse:
    try:
        return service.create_upload_url(
            file_name=body.file_name,
            content_type=body.content_type,
            file_size_bytes=body.file_size_bytes,
        )
    except InvalidContentTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileTooLargeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{submission_id}/start", response_model=StartProcessingResponse)
def start_processing(
    submission_id: str,
    body: StartProcessingRequest,
    service: SubmissionService = Depends(get_submission_service),
) -> StartProcessingResponse:
    try:
        return service.start_processing(submission_id, body.object_key)
    except SubmissionNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Submission {submission_id} not found"
        )


@router.get("/{submission_id}", response_model=SubmissionStatusResponse)
def get_submission_status(
    submission_id: str,
    service: SubmissionService = Depends(get_submission_service),
) -> SubmissionStatusResponse:
    try:
        return service.get_status(submission_id)
    except SubmissionNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Submission {submission_id} not found"
        )


@router.get("/{submission_id}/summary", response_model=SummaryResponse)
def get_submission_summary(
    submission_id: str,
    service: SubmissionService = Depends(get_submission_service),
) -> SummaryResponse:
    try:
        return service.get_summary(submission_id)
    except SubmissionNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Submission {submission_id} not found"
        )
    except SummaryNotAvailableError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("", response_model=SubmissionListResponse)
def list_submissions(
    status: SubmissionStatus | None = None,
    limit: int = Query(25, ge=1, le=MAX_LIST_LIMIT),
    next_token: str | None = Query(None, alias="nextToken"),
    service: SubmissionService = Depends(get_submission_service),
) -> SubmissionListResponse:
    return service.list_submissions(status=status, limit=limit, next_token=next_token)
