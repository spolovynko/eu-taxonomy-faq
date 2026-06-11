import json
import sys

from loguru import logger


def configure_logging() -> None:
    logger.remove()
    logger.add(_write_json)


def _write_json(message) -> None:
    record = message.record
    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        **record["extra"],
    }

    if record["exception"]:
        payload["exception"] = str(record["exception"])

    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()
