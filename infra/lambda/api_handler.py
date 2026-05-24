from __future__ import annotations

from mangum import Mangum

from risklens_api.api import deps
from risklens_api.core.config import get_settings
from risklens_api.main import app
from runtime_services import S3StorageService, SQSQueueService

settings = get_settings()

deps._storage = S3StorageService(region_name=settings.aws_region)  # noqa: SLF001
deps._queue = SQSQueueService(  # noqa: SLF001
    queue_url=settings.sqs_queue_url,
    region_name=settings.aws_region,
)
deps._service = None  # noqa: SLF001

handler = Mangum(app, lifespan="off")

