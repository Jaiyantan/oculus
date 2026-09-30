"""
Circuit breaker pattern — protects against AWS outage during demo.

States:
    CLOSED  -> normal, calls go through
    OPEN    -> failing, fail fast without calling
    HALF_OPEN -> testing recovery with a single call
"""
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_s: int = 30):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.opened_at = None

    def call(self, fn, *args, **kwargs):
        """
        Execute fn through the circuit breaker.

        In OPEN state, raises immediately without calling fn.
        In HALF_OPEN state, allows one test call.
        In CLOSED state, calls normally and tracks failures.
        """
        if self.state == CircuitState.OPEN:
            if time.time() - self.opened_at > self.recovery_timeout_s:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit OPEN: notification service unavailable")

        try:
            result = fn(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = time.time()
            raise
