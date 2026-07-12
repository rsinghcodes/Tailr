from contextvars import ContextVar

request_id: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)


def set_request_id(value: str):
    request_id.set(value)


def get_request_id() -> str | None:
    return request_id.get()


def clear_request_id():
    request_id.set(None)    