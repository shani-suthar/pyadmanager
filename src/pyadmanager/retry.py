"""Retry decorator for transient HTTP failures."""

import logging
import time
from functools import wraps

import requests

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def retry(max_retries: int = 3, base_delay: float = 1):
    """Retry a function on retryable HTTP status codes or transient network errors,
    with exponential backoff between attempts."""

    def decorator(func):
        func_name = getattr(func, "__qualname__", None) or repr(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except requests.HTTPError as e:
                    status_code = e.response.status_code if e.response is not None else None
                    if status_code not in RETRYABLE_STATUS_CODES:
                        logger.debug(
                            "%s: non-retryable HTTP error, raising immediately: %s",
                            func_name,
                            e,
                        )
                        raise
                    if attempt == max_retries:
                        logger.error(
                            "%s: giving up after %d attempt(s), HTTP %s: %s",
                            func_name,
                            attempt + 1,
                            status_code,
                            e,
                        )
                        raise
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        "%s: HTTP %s on attempt %d/%d, retrying in %.1fs",
                        func_name,
                        status_code,
                        attempt + 1,
                        max_retries + 1,
                        delay,
                    )
                    time.sleep(delay)

                except (
                    requests.ConnectionError,
                    requests.ConnectTimeout,
                    requests.ReadTimeout,
                    requests.exceptions.ChunkedEncodingError,
                ) as e:
                    if attempt == max_retries:
                        logger.error(
                            "%s: giving up after %d attempt(s): %s",
                            func_name,
                            attempt + 1,
                            e,
                        )
                        raise
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        "%s: %s on attempt %d/%d, retrying in %.1fs",
                        func_name,
                        e,
                        attempt + 1,
                        max_retries + 1,
                        delay,
                    )
                    time.sleep(delay)

        return wrapper

    return decorator
