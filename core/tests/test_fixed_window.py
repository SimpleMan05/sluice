import time
from core.fixed_window import FixedWindowCounter

def test_allows_requests_within_limit():
    limiter = FixedWindowCounter(limit=3, window_seconds=60)
    for _ in range(3):
        result = limiter.check("user1")
        assert result.allowed is True

    #4th request should be blocked
    result = limiter.check("user1")
    assert result.allowed is False
    assert result.remaining == 0

def test_different_keys_have_independent_counters():
    limiter = FixedWindowCounter(limit=1, window_seconds=60)
    result1 = limiter.check("user1")
    result2 = limiter.check("user2")
    assert result1.allowed is True
    assert result2.allowed is True  # different key, separate quota

def test_window_resets_after_expiry():
    limiter = FixedWindowCounter(limit=1, window_seconds=1)
    result1 = limiter.check("user1")
    assert result1.allowed is True

    result2 = limiter.check("user1")
    assert result2.allowed is False # limit hit within same window

    time.sleep(1.1) #wait for window to expire

    result3 = limiter.check("user1")
    assert result3.allowed is True #new window, counter reset