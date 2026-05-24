from enum import StrEnum


class SubmissionStatus(StrEnum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    OCR_RUNNING = "OCR_RUNNING"
    EXTRACTING = "EXTRACTING"
    ENRICHING = "ENRICHING"
    GENERATING_SUMMARY = "GENERATING_SUMMARY"
    READY = "READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAILED = "FAILED"


ALLOWED_CONTENT_TYPES = frozenset({
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
})

DEFAULT_MAX_FILE_SIZE_BYTES = 10_000_000  # 10 MB
DEFAULT_UPLOAD_EXPIRY_SECONDS = 900  # 15 min
DEFAULT_LIST_LIMIT = 25
MAX_LIST_LIMIT = 100
