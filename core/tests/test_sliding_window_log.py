import time
from core.sliding_window_log import SlidingWindowLog

def test_allows_requests_within_limit():
    limiter = SlidingWindowLog(limit=3, window_seconds=60)
    for _ in range(3):
        result = limiter.check("user1")
        assert result.allowed is True

    result = limiter.check("user1")
    assert result.allowed is False
    assert result.remaining == 0

def test_different_keys_have_independent_logs():
    limiter = SlidingWindowLog(limit=1, window_seconds=60)
    result1 = limiter.check("user1")
    result2 = limiter.check("user2")

    assert result1.allowed is True
    assert result2.allowed is True

def test_old_requests_expire_out_of_window():
    limiter = SlidingWindowLog(limit=1, window_seconds=1)
    result1 = limiter.check("user1")
    assert result1.allowed is True

    result2 = limiter.check("user1")
    assert result2.allowed is False #limit hit

    time.sleep(1.1)

    result3 = limiter.check("user1")
    assert result3.allowed is True # old timestamp expired out

def test_sliding_behaviour_is_smoother_than_sliding_window():
    """
    it demonstrates the key difference from Fixed Window: requests spread
    across a boundary don't cause a 2x burst, because the window
    slides continuously rather than resetting at fixed points.
    """

    limiter = SlidingWindowLog(limit = 2, window_seconds=1)

    assert limiter.check("user1").allowed is True
    assert limiter.check("user1").allowed is True
    assert limiter.check("user1").allowed is False #limit hit

    time.sleep(0.5) # halfway through the window, both old requests still active

    assert limiter.check("user1").allowed is False  # still blocked, window hasn't slid enough

    time.sleep(0.6)  # now t=1.1, both original requests have expired
    
    assert limiter.check("user1").allowed is True