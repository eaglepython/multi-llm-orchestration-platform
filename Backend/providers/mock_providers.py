import time
import os
from typing import Optional
import httpx
from providers.base import BaseLLMProvider, ProviderResponse

class OpenAIProvider(BaseLLMProvider):
“””
OpenAI GPT-4o-mini provider.
Uses httpx directly (no SDK dependency) so the routing logic stays visible.
“””

```
name = "OpenAI"
cost_per_1k_tokens = 0.00015  # GPT-4o-mini input pricing ($/1k tokens)
model = "gpt-4o-mini"

def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not self.api_key:
        raise ValueError("OPENAI_API_KEY not set")
    self.base_url = "https://api.openai.com/v1"
    self.headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
    }

async def complete(self, prompt: str, max_tokens: int = 512) -> ProviderResponse:
    payload = {
        "model": self.model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }

    start = time.monotonic()
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()

    latency_ms = int((time.monotonic() - start) * 1000)
    data = response.json()

    tokens = data["usage"]["total_tokens"]
    content = data["choices"][0]["message"]["content"]
    cost = self.compute_cost(tokens)

    self.stats.record_success(latency_ms, cost, tokens)

    return ProviderResponse(
        content=content,
        tokens_used=tokens,
        cost_usd=cost,
        latency_ms=latency_ms,
        model=self.model,
    )

async def health_check(self) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"{self.base_url}/models",
                headers=self.headers,
            )
            return r.status_code == 200
    except Exception:
        return False
```