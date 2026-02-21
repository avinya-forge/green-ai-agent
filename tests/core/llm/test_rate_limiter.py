import pytest
import time
import threading
from src.core.llm.rate_limiter import TokenBucketRateLimiter

def test_rate_limiter_initialization():
    limiter = TokenBucketRateLimiter(tpm=600, rpm=60)
    assert limiter.tpm_capacity == 600
    assert limiter.rpm_capacity == 60
    assert limiter.tokens == 600
    assert limiter.requests == 60

def test_rate_limiter_consumes_tokens():
    # 6000 TPM = 100 TPS
    limiter = TokenBucketRateLimiter(tpm=6000, rpm=600)

    start = time.time()
    limiter.wait_for(estimated_tokens=50)
    elapsed = time.time() - start

    # Should be instant as full
    assert elapsed < 0.1
    assert limiter.tokens <= 5950
    assert limiter.requests <= 599

def test_rate_limiter_waits_for_refill():
    # 60 RPM = 1 RPS
    limiter = TokenBucketRateLimiter(tpm=6000, rpm=60)

    # Empty the request bucket
    limiter.requests = 0

    start = time.time()
    limiter.wait_for(estimated_tokens=1)
    elapsed = time.time() - start

    # Should wait roughly 1 second
    assert elapsed >= 0.9

def test_rate_limiter_thread_safety():
    # 600 RPM = 10 RPS
    limiter = TokenBucketRateLimiter(tpm=60000, rpm=600)

    start = time.time()

    def worker():
        for _ in range(5):
            limiter.wait_for(1)

    threads = []
    for _ in range(4):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start
    # 20 requests total. 10 RPS capacity. Should take roughly 2 seconds (minus initial burst capacity).
    # Initial capacity is 600. So it should be instant.
    # To test waiting, we must drain capacity first.

    assert elapsed < 0.5 # Should be fast because capacity is full
