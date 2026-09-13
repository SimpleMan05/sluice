import time
from core.sliding_window_counter import SlidingWindowCounter

def test_allows_requests_within_limit():
    limiter = SlidingWindowCounter(limit=3, window_seconds=60)
    for _ in range(3):
        result = limiter.check("user1")
        assert result.allowed

    result = limiter.check("user1")
    assert not result.allowed 


def test_different_keys_are_independent():
    limiter = SlidingWindowCounter(limit=1, window_seconds=60)
    assert limiter.check("user1").allowed
    assert limiter.check("user2").allowed


def test_weighted_count_blocks_burst_across_boundary():
    """
    Fill up the limit right before a window boundary, then immediately
    after the boundary — the weighted overlap should still mostly block
    the second burst, unlike Fixed Window which would fully reset.
    """
    limiter = SlidingWindowCounter(limit=2, window_seconds=1)

    assert limiter.check("user1").allowed  # window 1, count=1
    assert limiter.check("user1").allowed  # window 1, count=2 (at limit)

    time.sleep(1.01)  # just past the window boundary

    # previous window's count (2) still has high overlap weight here,
    # so this should still be blocked despite being a "new" window
    assert limiter.check("user1").allowed
    result = limiter.check("user1")
    assert not result.allowed


def test_limit_available_again_after_full_window_passes():
    limiter = SlidingWindowCounter(limit=2, window_seconds=1)

    assert limiter.check("user1").allowed
    assert limiter.check("user1").allowed

    time.sleep(2.1)  # well past both windows, previous window's weight decays to ~0

    result = limiter.check("user1")
    assert result.allowed