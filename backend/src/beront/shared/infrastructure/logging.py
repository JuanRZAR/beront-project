import json
import logging
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "time": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "event": record.getMessage(),
                "request_id": getattr(record, "request_id", None),
                "exception_type": getattr(record, "exception_type", None),
            },
            ensure_ascii=False,
        )


def configure_logging(root, *, testing=False):
    logger = logging.getLogger("beront")
    logger.setLevel(logging.INFO)
    if not testing:
        root.mkdir(parents=True, exist_ok=True)
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()
        handler = RotatingFileHandler(
            root / "application.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
        )
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(JsonFormatter())
        logger.addHandler(console)
    return logger
