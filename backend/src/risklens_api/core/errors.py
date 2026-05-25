class RiskLensError(Exception):
    """Base exception for domain errors."""


class RetryableError(RiskLensError):
    """A transient failure that should be retried.

    Raised by pipeline-stage services for failures that are expected to
    succeed on a later attempt (throttling, timeouts, transient 5xx from
    AWS). The worker re-raises these so SQS redrive (and eventually the DLQ)
    handles retries. The worker must NOT set status FAILED on this error.
    """


class NonRetryableError(RiskLensError):
    """A permanent failure that must not be retried.

    Raised for validation failures or malformed inputs where retrying the
    same message cannot succeed (e.g. an unreadable/corrupt document). The
    worker treats this as terminal and sets status FAILED with a
    broker-readable reason.
    """


class SubmissionNotFoundError(RiskLensError):
    def __init__(self, submission_id: str) -> None:
        self.submission_id = submission_id
        super().__init__(f"Submission {submission_id} not found")


class InvalidContentTypeError(RiskLensError):
    def __init__(self, content_type: str) -> None:
        self.content_type = content_type
        super().__init__(f"Unsupported content type: {content_type}")


class FileTooLargeError(RiskLensError):
    def __init__(self, size: int, max_size: int) -> None:
        self.size = size
        self.max_size = max_size
        super().__init__(f"File size {size} exceeds maximum {max_size}")


class SummaryNotAvailableError(RiskLensError):
    def __init__(self, submission_id: str, status: str) -> None:
        self.submission_id = submission_id
        self.current_status = status
        super().__init__(
            f"Summary not available for submission {submission_id} in status {status}"
        )
