"""Thread-safe in-memory sliding-window rate limiter.

Zero external dependencies. Resets on server restart (acceptable for a
loopback-deployed tool that becomes a single public process).

Usage:
    limiter = RateLimiter(max_calls=5, window_seconds=60)
    if limiter.is_limited("192.168.1.1:login"):
        # return 429 Too Many Requests
"""

import threading
import time


class RateLimiter:
    """Sliding-window rate limiter keyed on arbitrary string identifiers."""

    def __init__(self, max_calls: int, window_seconds: int):
        self._max = max_calls
        self._window = window_seconds
        self._buckets: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def is_limited(self, key: str) -> bool:
        """Return True if *key* has exceeded the allowed rate."""
        now = time.monotonic()
        cutoff = now - self._window
        with self._lock:
            timestamps = self._buckets.get(key)
            if timestamps is None:
                self._buckets[key] = [now]
                return False
            # Evict expired timestamps
            timestamps = [t for t in timestamps if t > cutoff]
            if len(timestamps) >= self._max:
                self._buckets[key] = timestamps
                return True
            timestamps.append(now)
            self._buckets[key] = timestamps
            return False

    def reset(self, key: str) -> None:
        """Clear the rate-limit counter for *key* (e.g., after successful auth)."""
        with self._lock:
            self._buckets.pop(key, None)

    def purge_expired(self) -> None:
        """Remove all stale buckets. Call periodically to free memory."""
        now = time.monotonic()
        cutoff = now - self._window
        with self._lock:
            stale = [k for k, ts in self._buckets.items() if all(t <= cutoff for t in ts)]
            for k in stale:
                del self._buckets[k]


# Shared limiters — imported by server.py
# Login / signup: 10 attempts per IP per 10 minutes
auth_limiter = RateLimiter(max_calls=10, window_seconds=600)

# Password reset request: 5 per IP per 15 minutes
reset_request_limiter = RateLimiter(max_calls=5, window_seconds=900)

# General API: 300 requests per IP per minute
api_limiter = RateLimiter(max_calls=300, window_seconds=60)
