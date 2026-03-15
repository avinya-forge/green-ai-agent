import time
from threading import Lock


class TokenBucketRateLimiter:
    """
    Thread-safe rate limiter using the Token Bucket algorithm.
    Enforces both Tokens Per Minute (TPM) and Requests Per Minute (RPM).
    """

    def __init__(self, tpm: int, rpm: int):
        """
        Initialize the rate limiter.

        Args:
            tpm: Tokens Per Minute capacity.
            rpm: Requests Per Minute capacity.
        """
        self.tpm_capacity = float(tpm)
        self.rpm_capacity = float(rpm)

        # Current bucket levels (start full)
        self.tokens = self.tpm_capacity
        self.requests = self.rpm_capacity

        self.last_check = time.time()
        self.lock = Lock()

    def _refill(self):
        """
        Refill buckets based on elapsed time.
        """
        now = time.time()
        elapsed = now - self.last_check

        if elapsed <= 0:
            return

        # Refill tokens
        token_refill = elapsed * (self.tpm_capacity / 60.0)
        self.tokens = min(self.tpm_capacity, self.tokens + token_refill)

        # Refill requests
        req_refill = elapsed * (self.rpm_capacity / 60.0)
        self.requests = min(self.rpm_capacity, self.requests + req_refill)

        self.last_check = now

    def wait_for(self, estimated_tokens: int = 0):
        """
        Block until sufficient capacity is available.

        Args:
            estimated_tokens: The estimated number of tokens this request will consume.
                              If unknown, use a reasonable default or 0 (and only limit RPM).
        """
        while True:
            with self.lock:
                self._refill()

                # Check if we have enough for 1 request and N tokens
                if self.requests >= 1.0 and self.tokens >= estimated_tokens:
                    self.requests -= 1.0
                    self.tokens -= estimated_tokens
                    return

                # Calculate how long to wait
                req_shortage = 1.0 - self.requests
                token_shortage = estimated_tokens - self.tokens

                wait_req = 0.0
                if req_shortage > 0:
                    # Time = amount / rate
                    # Rate = capacity / 60
                    wait_req = req_shortage / (self.rpm_capacity / 60.0)

                wait_tok = 0.0
                if token_shortage > 0:
                    wait_tok = token_shortage / (self.tpm_capacity / 60.0)

                # Determine max wait time needed
                wait_time = max(wait_req, wait_tok)

                # Ensure we don't spin too fast, but also don't wait 0 if logic says wait
                if wait_time < 0.01:
                    wait_time = 0.01

            # Sleep outside the lock
            time.sleep(wait_time)
