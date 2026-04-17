from __future__ import annotations

from tenacity import retry, stop_after_attempt, wait_exponential


class RetryPolicy:
    @staticmethod
    def with_backoff(attempts: int = 3):
        return retry(
            reraise=True,
            stop=stop_after_attempt(attempts),
            wait=wait_exponential(multiplier=1, min=1, max=30),
        )
