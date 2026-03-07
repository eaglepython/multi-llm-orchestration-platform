from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class ProviderStats:
“”“Live stats tracked per provider during runtime.”””
total_requests: int = 0
successful_requests: int = 0
failed_requests: int = 0
total_latency_ms: float = 0.0
total_cost_usd: float = 0.0
total_tokens: int = 0
consecutive_failures: int = 0
last_failure_time: Optional[float] = None

```
@property
def success_rate(self) -> float:
    if self.total_requests == 0:
        return 1.0
    return self.successful_requests / self.total_requests

@property
def avg_latency_ms(self) -> float:
    if self.successful_requests == 0:
        return 9999.0  # Penalize unknown latency in routing
    return self.total_latency_ms / self.successful_requests

def is_circuit_open(self) -> bool:
    """Circuit breaker: pause provider after 3 consecutive failures."""
    if self.consecutive_failures < 3:
        return False
    # Re-allow after 60 seconds
    if self.last_failure_time and (time.time() - self.last_failure_time) > 60:
        self.consecutive_failures = 0
        return False
    return True

def record_success(self, latency_ms: float, cost_usd: float, tokens: int):
    self.total_requests += 1
    self.successful_requests += 1
    self.total_latency_ms += latency_ms
    self.total_cost_usd += cost_usd
    self.total_tokens += tokens
    self.consecutive_failures = 0

def record_failure(self):
    self.total_requests += 1
    self.failed_requests += 1
    self.consecutive_failures += 1
    self.last_failure_time = time.time()
```

@dataclass
class ProviderResponse:
content: str
tokens_used: int
cost_usd: float
latency_ms: int
model: str

class BaseLLMProvider(ABC):
“””
Abstract base for all LLM providers.
Each provider implements complete() and reports its cost_per_1k_tokens.
The router never needs to know provider internals beyond this interface.
“””

```
name: str
cost_per_1k_tokens: float  # Used by router for cost scoring
stats: ProviderStats

def __init__(self):
    self.stats = ProviderStats()

@abstractmethod
async def complete(self, prompt: str, max_tokens: int) -> ProviderResponse:
    """Send prompt, return structured response. Raise on any error."""
    pass

@abstractmethod
async def health_check(self) -> bool:
    """Quick ping to verify provider is reachable."""
    pass

def compute_cost(self, tokens: int) -> float:
    return (tokens / 1000) * self.cost_per_1k_tokens
```