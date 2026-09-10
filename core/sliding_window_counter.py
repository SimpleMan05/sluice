import time
from core.strategy import RateLimitResult,RateLimiterStrategy

class SlidingWindowCounter(RateLimiterStrategy):
    def __init__(self, limit:int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds

        #key->(current_window_start, current_count, previous_count)
        self._state: dict[str, tuple[float, int ,int]] = {}

    def check(self, key:str) -> RateLimitResult:
        now = time.time()
        current_window_start, current_count, previous_count = self._state.get(
            key, (now,0,0)
        )

        elapsed = now - current_window_start

        if elapsed >= self.window_seconds:
            #How many full windows have passed
            windows_passed = int(elapsed // self.window_seconds)

            if windows_passed == 1:
                #current window becomes the previous window
                previous_count = current_count
            else:
                #More than one window passed with no activity - previous window is stale
                previous_count = 0

            current_count = 0
            current_window_start += windows_passed*self.window_seconds
            elapsed = now - current_window_start

        overlap = max(0.0, (self.window_seconds-elapsed)/self.window_seconds)
        estimated_count = previous_count * overlap + current_count

        if estimated_count < self.limit:
            current_count += 1
            self._state[key] = (current_window_start, current_count, previous_count)
            remaining = int(self.limit - (estimated_count + 1))
            return RateLimitResult(allowed=True, remaining= max(0, remaining))

        else:
            retry_after = self.window_seconds - elapsed
            return RateLimitResult(allowed=False, remaining=0, retry_after=retry_after)