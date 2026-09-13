from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: float | None = None

class RateLimiterStrategy(ABC):
    """
    This is a common interface all rate limiting algorithms must implement.
    """

    @abstractmethod
    def check(self, key:str)-> RateLimitResult:
        """
        check whether a request for 'key' is allowed right now. 
        Implementations should update internal state (consume quota) as part of this call.
        """
        raise NotImplementedError