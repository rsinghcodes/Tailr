import asyncio
import random
from typing import Callable, Any, TypeVar

T = TypeVar("T")


class RetryPolicy:
    """Exponential backoff with jitter retry strategy."""

    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0, max_delay: float = 10.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    async def execute_async(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        delay = self.initial_delay
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                last_exception = err
                if attempt == self.max_retries:
                    raise err

                jitter = random.uniform(0, 0.1 * delay)
                sleep_time = min(delay + jitter, self.max_delay)
                await asyncio.sleep(sleep_time)
                delay *= self.backoff_factor

        if last_exception:
            raise last_exception
