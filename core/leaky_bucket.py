import time
from core.strategy import RateLimitResult, RateLimiterStrategy

class LeakyBucket(RateLimiterStrategy):
    def __init__(self, capacity:int, leak_rate: float):
        """
        capacity: max 'water level' the bucket can hold before overflowing
        leak_rate: units processed per second
        """
        self.capacity = capacity
        self.leak_rate = leak_rate

        #key->(current_level, last_check_timestamp)
        self._buckets: dict[str, tuple[float, float]] = {}

    def check(self, key:str) -> RateLimitResult:
        now = time.time()
        level, last_check = self._buckets.get(key,(0.0,now))

        #leak based on time elapsed since last check
        elapsed = now - last_check
        leaked_amount = elapsed * self.leak_rate
        level = max(0.0, level - leaked_amount)

        if level+1 <= self.capacity:
            level+=1
            self._buckets[key] = (level, now)
            remaining = int(self.capacity - level)
            return RateLimitResult(allowed=True, remaining=remaining)
        else:
            self._buckets[key] = (level,now)
            overflow_amount = (level + 1) - self.capacity
            retry_after = overflow_amount/self.leak_rate
            return RateLimitResult(allowed=False, remaining=0, retry_after=retry_after)

        