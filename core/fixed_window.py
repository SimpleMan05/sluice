import time
from core.strategy import RateLimiterStrategy, RateLimitResult

class FixedWindowCounter(RateLimiterStrategy):
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        #key->(window_start_timestamp, count)
        self._counters: dict[str, tuple[float,int]] = {}

    def check(self, key:str) -> RateLimitResult:
        now = time.time()
        window_start, count = self._counters.get(key,(now,0))

        #if current window has expired, start a new one
        if now - window_start >= self.window_seconds:
            window_start = now
            count = 0

        if count < self.limit:
            count+= 1
            self._counters[key] = (window_start, count)
            remaining = self.limit - count
            return RateLimitResult(allowed=True, remaining=remaining)
        else:
            retry_after = self.window_seconds - (now - window_start)
            return RateLimitResult(allowed=False, remaining=0, retry_after=retry_after)

