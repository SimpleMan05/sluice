import time
from core.token_bucket import TokenBucket

def test_allows_burst_up_to_capacity():
    limiter = TokenBucket(capacity=3, refill_rate=1)

    for _ in range(3):
        assert limiter.check("user1").allowed is True

    #bucket now empty
    assert limiter.check("user1").allowed is False

def test_different_keys_have_independent_buckets():
    limiter = TokenBucket(capacity=1, refill_rate=1)
    assert limiter.check("user1").allowed is True
    assert limiter.check("user2").allowed is True
    assert limiter.check("user1").allowed is False

def test_tokens_refill_over_time():
    limiter = TokenBucket(capacity=1, refill_rate=1)
    assert limiter.check("user1").allowed is True
    assert not limiter.check("user1").allowed

    time.sleep(1.1)

    assert limiter.check("user1").allowed #token refilled

def test_bucket_does_not_overflow_past_capacity():
    limiter = TokenBucket(capacity=2, refill_rate=5)
    time.sleep(1)

    allowed_count = sum(1 for _ in range(5) if limiter.check("user1").allowed)

    assert allowed_count == 2
