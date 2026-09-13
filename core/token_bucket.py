import time
from core.strategy import RateLimitResult, RateLimiterStrategy

class TokenBucket(RateLimiterStrategy):
    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity: max tokens the bucket can hold(the max burst size)
        refill_rate: tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate

        #key->(tokens_available, last_refill_timestamp)
        self._buckets: dict[str, tuple[float, float]] = {}

    def check(self, key:str) -> RateLimitResult:
        now = time.time()
        tokens, last_refill = self._buckets.get(key, (self.capacity,now))

        #Refill based on time elapsed since last check
        elapsed = now - last_refill
        refill_amount = elapsed * self.refill_rate

        tokens = min(self.capacity, tokens+refill_amount)

        if tokens >= 1:
            tokens -= 1
            self._buckets[key] = (tokens,now)
            return RateLimitResult(allowed=True, remaining=int(tokens))
        else:
            self._buckets[key] = (tokens,now)
            tokens_needed = 1 - tokens
            retry_after = tokens_needed/self.refill_rate
            return RateLimitResult(allowed=False, remaining=0, retry_after=retry_after)
