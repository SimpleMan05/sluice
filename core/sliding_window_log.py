import time
from collections import deque
from core.strategy import RateLimitResult, RateLimiterStrategy

class SlidingWindowLog(RateLimiterStrategy):
    def __init__ (self, limit:int, window_seconds:int) : 
        self.limit = limit
        self.window_seconds = window_seconds

        #key -> deque of request timestamps
        self._logs: dict[str, deque[float]] = {}

    def check(self, key:str) -> RateLimitResult:
        now = time.time()
        log = self._logs.setdefault(key, deque())

        #remove timestamps that have fallen outside the window
        while log and now - log[0] >= self.window_seconds:
            log.popleft()

        if len(log) < self.limit:
            log.append(now)
            remaining = self.limit - len(log)
            return RateLimitResult(allowed=True, remaining=remaining)
        else:
            oldest = log[0]
            retry_after = self.window_seconds - (now-oldest)
            return RateLimitResult(allowed=False, remaining=0, retry_after=retry_after)