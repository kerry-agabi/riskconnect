from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    records = event.get("Records", [])
    for record in records:
        logger.info(
            "Received processing message",
            extra={"message_id": record.get("messageId")},
        )
        try:
            payload = json.loads(record.get("body", "{}"))
        except json.JSONDecodeError:
            payload = {"raw_body": record.get("body")}
        logger.info("Processing placeholder complete", extra={"payload": payload})

    return {"processed": len(records)}

