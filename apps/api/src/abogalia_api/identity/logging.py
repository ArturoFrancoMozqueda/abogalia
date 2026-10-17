"""Prevent rejected private URLs from becoming an access-log credential sink."""

import logging
from urllib.parse import unquote


class AuthAccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Uvicorn emits request line as args[2]; do not format/log discarded values.
        if isinstance(record.args, tuple) and len(record.args) >= 3:
            line = record.args[2]
            if isinstance(line, str):
                decoded = unquote(line)
                if any(
                    prefix in decoded
                    for prefix in (
                        "/api/auth",
                        "/api/professional",
                        "/api/public/professionals",
                        "/api/legal-requests",
                    )
                ):
                    return False
        return True


def configure_identity_logging():
    logger = logging.getLogger("uvicorn.access")
    if not any(isinstance(item, AuthAccessFilter) for item in logger.filters):
        logger.addFilter(AuthAccessFilter())
    # No third-party HTTP debug diagnostics in this authentication process.
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
