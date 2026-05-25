from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "infra" / "lambda"))

import worker_handler
from risklens_api.core.errors import RetryableError
from risklens_api.core.constants import SubmissionStatus


class StubProcessor:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.messages = []

    def process(self, message, correlation_id: str):  # type: ignore[no-untyped-def]
        self.messages.append((message, correlation_id))
        if self.error:
            raise self.error
        return SubmissionStatus.READY


def _event(*bodies: str) -> dict:
    return {
        "Records": [
            {"messageId": f"msg-{i}", "body": body}
            for i, body in enumerate(bodies, start=1)
        ]
    }


def test_handler_returns_no_failures_for_valid_messages(monkeypatch: pytest.MonkeyPatch) -> None:
    processor = StubProcessor()
    monkeypatch.setattr(worker_handler, "_get_processor", lambda: processor)

    result = worker_handler.handler(
        _event(json.dumps({"submission_id": "SUB-1", "object_key": "raw/a.pdf"})),
        object(),
    )

    assert result == {"batchItemFailures": []}
    assert processor.messages[0][1] == "msg-1"


def test_handler_reports_retryable_message_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    processor = StubProcessor(error=RetryableError("try again"))
    monkeypatch.setattr(worker_handler, "_get_processor", lambda: processor)

    result = worker_handler.handler(
        _event(json.dumps({"submission_id": "SUB-1", "object_key": "raw/a.pdf"})),
        object(),
    )

    assert result == {"batchItemFailures": [{"itemIdentifier": "msg-1"}]}


def test_handler_reports_invalid_json_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    processor = StubProcessor()
    monkeypatch.setattr(worker_handler, "_get_processor", lambda: processor)

    result = worker_handler.handler(_event("{not-json"), object())

    assert result == {"batchItemFailures": [{"itemIdentifier": "msg-1"}]}
    assert processor.messages == []


def test_handler_reports_only_failed_records(monkeypatch: pytest.MonkeyPatch) -> None:
    class MixedProcessor(StubProcessor):
        def process(self, message, correlation_id: str):  # type: ignore[no-untyped-def]
            super().process(message, correlation_id)
            if correlation_id == "msg-2":
                raise RetryableError("try again")
            return SubmissionStatus.READY

    processor = MixedProcessor()
    monkeypatch.setattr(worker_handler, "_get_processor", lambda: processor)

    result = worker_handler.handler(
        _event(
            json.dumps({"submission_id": "SUB-1", "object_key": "raw/a.pdf"}),
            json.dumps({"submission_id": "SUB-2", "object_key": "raw/b.pdf"}),
        ),
        object(),
    )

    assert result == {"batchItemFailures": [{"itemIdentifier": "msg-2"}]}
