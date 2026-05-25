from __future__ import annotations

from mangum import Mangum

from risklens_api.api import deps
from risklens_api.core.config import get_settings
from risklens_api.main import app
from runtime_services import DynamoSubmissionService, S3StorageService, SQSQueueService

settings = get_settings()

storage = S3StorageService(region_name=settings.aws_region)
queue = SQSQueueService(
    queue_url=settings.sqs_queue_url,
    region_name=settings.aws_region,
)
deps._storage = storage  # noqa: SLF001
deps._queue = queue  # noqa: SLF001
deps._service = DynamoSubmissionService(  # noqa: SLF001
    settings=settings,
    storage=storage,
    queue=queue,
    table_name=settings.submissions_table,
    region_name=settings.aws_region,
)

handler = Mangum(app, lifespan="off")
