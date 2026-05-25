from __future__ import annotations

import json
import os
from typing import Any

from pydantic import ValidationError

from risklens_api.core.config import get_settings
from risklens_api.core.errors import RetryableError
from risklens_api.core.logging import get_logger
from risklens_api.schemas.processing import ProcessingMessage
from risklens_api.services.enrichment_service import HazardEnrichmentService
from risklens_api.worker.processor import SubmissionProcessor
from runtime_services import (
    BedrockFieldExtractionService,
    CensusGeocodeService,
    DynamoHazardRepository,
    DynamoStatusStore,
    DynamoSummaryGenerationService,
    TextractTextExtractionService,
)

_logger = get_logger()
_processor: SubmissionProcessor | None = None


def _build_processor() -> SubmissionProcessor:
    settings = get_settings()
    region = settings.aws_region
    submissions_table = settings.submissions_table
    hazards_table = settings.hazards_table
    bucket = settings.s3_bucket

    return SubmissionProcessor(
        status_store=DynamoStatusStore(submissions_table, region),
        text_extraction=TextractTextExtractionService(bucket, region),
        field_extraction=BedrockFieldExtractionService(
            bucket=bucket,
            region_name=region,
            model_id=settings.bedrock_model_id,
            max_input_chars=settings.bedrock_max_input_chars,
            max_output_tokens=int(os.environ.get("BEDROCK_EXTRACTION_MAX_TOKENS", "800")),
        ),
        enrichment=HazardEnrichmentService(
            geocoder=CensusGeocodeService(),
            hazards=DynamoHazardRepository(hazards_table, region),
        ),
        summary_generation=DynamoSummaryGenerationService(
            table_name=submissions_table,
            region_name=region,
            model_id=settings.bedrock_model_id,
            max_output_tokens=int(os.environ.get("BEDROCK_BRIEF_MAX_TOKENS", "1000")),
        ),
    )


def _get_processor() -> SubmissionProcessor:
    global _processor  # noqa: PLW0603
    if _processor is None:
        _processor = _build_processor()
    return _processor


def handler(event: dict[str, Any], context: object) -> dict[str, list[dict[str, str]]]:
    """Process an SQS batch and report partial failures back to Lambda."""
    failures: list[dict[str, str]] = []
    processor = _get_processor()

    for record in event.get("Records", []):
        message_id = record.get("messageId", "")
        try:
            body = json.loads(record.get("body", "{}"))
            message = ProcessingMessage.model_validate(body)
            processor.process(message, correlation_id=message_id)
        except (json.JSONDecodeError, ValidationError) as exc:
            _logger.warning(
                "Invalid SQS processing message; leaving for redrive",
                extra={"component": "worker_handler", "message_id": message_id},
                exc_info=exc,
            )
            failures.append({"itemIdentifier": message_id})
        except RetryableError as exc:
            _logger.warning(
                "Retryable worker failure; reporting batch item failure",
                extra={"component": "worker_handler", "message_id": message_id},
                exc_info=exc,
            )
            failures.append({"itemIdentifier": message_id})
        except Exception:  # noqa: BLE001 - unknown failures should retry
            _logger.exception(
                "Unexpected worker failure; reporting batch item failure",
                extra={"component": "worker_handler", "message_id": message_id},
            )
            failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failures}
