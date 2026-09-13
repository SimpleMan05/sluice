import time
from core.leaky_bucket import LeakyBucket


def test_allows_requests_up_to_capacity():
    limiter = LeakyBucket(capacity=3, leak_rate=1)  # leaks 1/sec
    for _ in range(3):
        assert limiter.check("user1").allowed
    # bucket now full
    assert not limiter.check("user1").allowed


def test_different_keys_have_independent_buckets():
    limiter = LeakyBucket(capacity=1, leak_rate=1)
    assert limiter.check("user1").allowed
    assert limiter.check("user2").allowed


def test_bucket_leaks_over_time():
    limiter = LeakyBucket(capacity=1, leak_rate=1)  # 1 unit/sec leak
    assert limiter.check("user1").allowed  # bucket now full (level=1)
    assert not limiter.check("user1").allowed  # still full

    time.sleep(1.1)  # enough time to leak out

    assert limiter.check("user1").allowed  # space freed up


def test_smooths_burst_unlike_token_bucket():
    """
    Even with a burst of requests, the bucket only allows up to capacity,
    then requires waiting for the steady leak rate to free up space —
    demonstrating the smoothing behavior Leaky Bucket is known for.
    """
    limiter = LeakyBucket(capacity=2, leak_rate=1)
    assert limiter.check("user1").allowed
    assert limiter.check("user1").allowed
    assert not limiter.check("user1").allowed  # burst beyond capacity rejected

    time.sleep(0.5)  # only half a unit has leaked, not enough for a full slot
    assert not limiter.check("user1").allowed

    time.sleep(0.6)  # now ~1.1s total elapsed, enough for one slot to free up
    assert limiter.check("user1").allowed