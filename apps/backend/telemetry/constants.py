from typing import Final

LOGGER_NAME: Final = "tailr"

REQUEST_ID_HEADER: Final = "X-Request-ID"

LOG_FORMAT: Final = (
    "%(asctime)s "
    "%(levelname)s "
    "%(name)s "
    "%(request_id)s "
    "%(message)s"
)