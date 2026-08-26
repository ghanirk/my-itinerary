
import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """Sliding-window rate limiter per key (mis. per IP, atau IP+email)."""

    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        """Raise HTTP 429 kalau `key` sudah melebihi batas percobaan dalam window."""
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            cutoff = now - self.window_seconds
            hits[:] = [t for t in hits if t > cutoff]
            if len(hits) >= self.max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Terlalu banyak percobaan. Coba lagi dalam beberapa menit.",
                )
            hits.append(now)


login_limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=300)
register_limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=300)


def rate_limit_key(request: Request, extra: str | None = None) -> str:
    """Bikin key limiter dari IP request, opsional digabung dengan field lain (mis. email)."""
    ip = request.client.host if request.client else "unknown"
    return f"{ip}:{extra}" if extra else ip
