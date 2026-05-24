from __future__ import annotations

import json
from typing import Any

import boto3


class S3StorageService:
    def __init__(self, region_name: str) -> None:
        self._client = boto3.client("s3", region_name=region_name)

    def generate_presigned_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        expires_in: int,
    ) -> str:
        return self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )


class SQSQueueService:
    def __init__(self, queue_url: str, region_name: str) -> None:
        self._queue_url = queue_url
        self._client = boto3.client("sqs", region_name=region_name)

    def send_processing_message(self, submission_id: str, object_key: str) -> None:
        if not self._queue_url:
            return

        body: dict[str, Any] = {
            "submission_id": submission_id,
            "object_key": object_key,
        }
        self._client.send_message(
            QueueUrl=self._queue_url,
            MessageBody=json.dumps(body),
        )

