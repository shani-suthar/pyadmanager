"""Retry decorator for transient HTTP failures."""

import time
from functools import wraps

import requests

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def retry(max_retries: int = 3, base_delay: float = 1):
    """Retry a function on retryable HTTP status codes or transient network errors,
    with exponential backoff between attempts."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except requests.HTTPError as e:
                    if e.response is None or e.response.status_code not in RETRYABLE_STATUS_CODES:
                        raise
                    if attempt == max_retries:
                        raise
                    time.sleep(base_delay * (2**attempt))

                except (
                    requests.ConnectionError,
                    requests.ConnectTimeout,
                    requests.ReadTimeout,
                    requests.exceptions.ChunkedEncodingError,
                ):
                    if attempt == max_retries:
                        raise
                    time.sleep(base_delay * (2**attempt))

        return wrapper

    return decorator
