“””
Mock providers for Anthropic Claude and Google Gemini.

These simulate realistic latency, cost, and occasional failures so the
routing engine can be fully exercised without additional API keys.
In production, replace complete() with real API calls — the interface
is identical to OpenAIProvider.
“””

import asyncio
import random
import time
from providers.base import BaseLLMProvider, ProviderResponse

class AnthropicProvider(BaseLLMProvider):
“””
Simulated Anthropic Claude Haiku provider.
Cost: $0.00025/1k tokens | Avg latency: ~180ms | Reliability: 99.4%
“””

```
name = "Anthropic"
cost_per_1k_tokens = 0.00025
model = "claude-haiku-3-simulated"

def __init__(self):
    super().__init__()
    # Simulate occasional degradation
    self._failure_rate = 0.006  # 0.6% failure rate

async def complete(self, prompt: str, max_tokens: int = 512) -> ProviderResponse:
    # Simulate network latency (150–220ms range, occasionally spikes)
    latency_ms = int(random.gauss(180, 25))
    latency_ms = max(100, min(latency_ms, 500))
    await asyncio.sleep(latency_ms / 1000)

    if random.random() < self._failure_rate:
        self.stats.record_failure()
        raise ConnectionError("Anthropic: simulated transient error")

    tokens = len(prompt.split()) + max_tokens // 2
    cost = self.compute_cost(tokens)
    content = f"[Anthropic Claude] Response to: '{prompt[:60]}...'"

    self.stats.record_success(latency_ms, cost, tokens)
    return ProviderResponse(
        content=content,
        tokens_used=tokens,
        cost_usd=cost,
        latency_ms=latency_ms,
        model=self.model,
    )

async def health_check(self) -> bool:
    await asyncio.sleep(0.05)
    return random.random() > 0.01  # 99% uptime
```

class GeminiProvider(BaseLLMProvider):
“””
Simulated Google Gemini Flash provider.
Cost: $0.000075/1k tokens | Avg latency: ~160ms | Reliability: 98.9%
“””

```
name = "Gemini"
cost_per_1k_tokens = 0.000075  # Cheapest in the pool
model = "gemini-1.5-flash-simulated"

def __init__(self):
    super().__init__()
    self._failure_rate = 0.011  # Slightly higher failure rate

async def complete(self, prompt: str, max_tokens: int = 512) -> ProviderResponse:
    latency_ms = int(random.gauss(160, 30))
    latency_ms = max(90, min(latency_ms, 450))
    await asyncio.sleep(latency_ms / 1000)

    if random.random() < self._failure_rate:
        self.stats.record_failure()
        raise ConnectionError("Gemini: simulated transient error")

    tokens = len(prompt.split()) + max_tokens // 2
    cost = self.compute_cost(tokens)
    content = f"[Google Gemini] Response to: '{prompt[:60]}...'"

    self.stats.record_success(latency_ms, cost, tokens)
    return ProviderResponse(
        content=content,
        tokens_used=tokens,
        cost_usd=cost,
        latency_ms=latency_ms,
        model=self.model,
    )

async def health_check(self) -> bool:
    await asyncio.sleep(0.05)
    return random.random() > 0.02
```