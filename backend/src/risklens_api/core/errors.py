class RiskLensError(Exception):
    """Base exception for domain errors."""


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
