“””
router.py — Core LLM Routing Engine

This is the brain of the platform. Given a request and a strategy,
it scores every available provider and selects the best one.
Falls back automatically if the selected provider fails.

## Routing Strategies

CHEAPEST     : minimize cost_per_1k_tokens (ignores latency)
FASTEST      : minimize avg_latency_ms (ignores cost)
BALANCED     : weighted composite score (default, recommended)
ROUND_ROBIN  : cycle through providers regardless of performance

## Balanced Score Formula

score = (cost_weight * norm_cost) + (latency_weight * norm_latency) + (reliability_weight * norm_reliability)
Lower score = better provider. Scores are normalized 0→1 across the pool.
“””

import asyncio
import logging
from typing import Optional

from models import RoutingStrategy, RoutingDecision
from providers.base import BaseLLMProvider, ProviderResponse

logger = logging.getLogger(**name**)

# Balanced strategy weights (must sum to 1.0)

COST_WEIGHT = 0.45
LATENCY_WEIGHT = 0.35
RELIABILITY_WEIGHT = 0.20

class RoutingEngine:

```
def __init__(self, providers: list[BaseLLMProvider]):
    self.providers = providers
    self._round_robin_index = 0

# ------------------------------------------------------------------
# Public interface
# ------------------------------------------------------------------

async def route(
    self,
    prompt: str,
    max_tokens: int,
    strategy: RoutingStrategy,
    preferred_provider: Optional[str] = None,
    fallback_enabled: bool = True,
) -> tuple[ProviderResponse, RoutingDecision]:
    """
    Select a provider, call it, and return the response + routing decision.
    If the call fails and fallback_enabled, try remaining providers in order.
    """
    available = self._available_providers()
    if not available:
        raise RuntimeError("No providers available — all circuits open.")

    # Honor explicit preference if provider is available
    if preferred_provider:
        preferred = next(
            (p for p in available if p.name.lower() == preferred_provider.lower()),
            None,
        )
        if preferred:
            available = [preferred] + [p for p in available if p is not preferred]

    ordered, decision = self._rank_providers(available, strategy)

    # Try providers in ranked order
    fallback_triggered = False
    last_error: Optional[Exception] = None

    for i, provider in enumerate(ordered):
        try:
            logger.info(f"Routing to {provider.name} (attempt {i+1})")
            response = await provider.complete(prompt, max_tokens)

            if i > 0:
                fallback_triggered = True
                decision.selected_provider = provider.name
                decision.reason = f"Fallback from {ordered[0].name}: {last_error}"

            return response, decision, fallback_triggered, str(last_error) if fallback_triggered else None

        except Exception as e:
            logger.warning(f"{provider.name} failed: {e}")
            provider.stats.record_failure()
            last_error = e

            if not fallback_enabled:
                raise

    raise RuntimeError(f"All providers failed. Last error: {last_error}")

async def health_check_all(self) -> dict[str, bool]:
    """Run health checks on all providers concurrently."""
    tasks = {p.name: p.health_check() for p in self.providers}
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    return {
        name: (result is True)
        for name, result in zip(tasks.keys(), results)
    }

# ------------------------------------------------------------------
# Ranking logic
# ------------------------------------------------------------------

def _rank_providers(
    self,
    providers: list[BaseLLMProvider],
    strategy: RoutingStrategy,
) -> tuple[list[BaseLLMProvider], RoutingDecision]:

    if strategy == RoutingStrategy.ROUND_ROBIN:
        return self._round_robin(providers)

    scored = self._score_providers(providers, strategy)
    scored.sort(key=lambda x: x[1])  # Lower score = better

    ordered = [p for p, _ in scored]
    winner, winner_score = scored[0]

    decision = RoutingDecision(
        selected_provider=winner.name,
        reason=self._explain(winner, strategy),
        score=round(winner_score, 4),
        alternatives_considered=[
            {
                "provider": p.name,
                "score": round(s, 4),
                "cost_per_1k": p.cost_per_1k_tokens,
                "avg_latency_ms": round(p.stats.avg_latency_ms, 1),
                "success_rate": round(p.stats.success_rate, 4),
            }
            for p, s in scored[1:]
        ],
    )

    return ordered, decision

def _score_providers(
    self,
    providers: list[BaseLLMProvider],
    strategy: RoutingStrategy,
) -> list[tuple[BaseLLMProvider, float]]:

    if strategy == RoutingStrategy.CHEAPEST:
        return [(p, p.cost_per_1k_tokens) for p in providers]

    if strategy == RoutingStrategy.FASTEST:
        return [(p, p.stats.avg_latency_ms) for p in providers]

    # BALANCED: normalize each dimension then combine
    costs = [p.cost_per_1k_tokens for p in providers]
    latencies = [p.stats.avg_latency_ms for p in providers]
    # Reliability: invert so higher reliability = lower (better) score
    unreliabilities = [1 - p.stats.success_rate for p in providers]

    def normalize(values: list[float]) -> list[float]:
        lo, hi = min(values), max(values)
        if hi == lo:
            return [0.5] * len(values)
        return [(v - lo) / (hi - lo) for v in values]

    norm_costs = normalize(costs)
    norm_latencies = normalize(latencies)
    norm_unreliabilities = normalize(unreliabilities)

    scored = []
    for i, p in enumerate(providers):
        score = (
            COST_WEIGHT * norm_costs[i]
            + LATENCY_WEIGHT * norm_latencies[i]
            + RELIABILITY_WEIGHT * norm_unreliabilities[i]
        )
        scored.append((p, score))

    return scored

def _round_robin(
    self, providers: list[BaseLLMProvider]
) -> tuple[list[BaseLLMProvider], RoutingDecision]:
    idx = self._round_robin_index % len(providers)
    self._round_robin_index += 1
    winner = providers[idx]
    ordered = [winner] + [p for p in providers if p is not winner]
    decision = RoutingDecision(
        selected_provider=winner.name,
        reason="Round-robin rotation",
        score=0.0,
        alternatives_considered=[],
    )
    return ordered, decision

def _available_providers(self) -> list[BaseLLMProvider]:
    """Filter out providers with open circuit breakers."""
    return [p for p in self.providers if not p.stats.is_circuit_open()]

@staticmethod
def _explain(provider: BaseLLMProvider, strategy: RoutingStrategy) -> str:
    if strategy == RoutingStrategy.CHEAPEST:
        return f"Lowest cost: ${provider.cost_per_1k_tokens}/1k tokens"
    if strategy == RoutingStrategy.FASTEST:
        return f"Lowest latency: {provider.stats.avg_latency_ms:.0f}ms avg"
    return (
        f"Best balanced score — "
        f"cost=${provider.cost_per_1k_tokens}/1k, "
        f"latency={provider.stats.avg_latency_ms:.0f}ms, "
        f"reliability={provider.stats.success_rate:.1%}"
    )
```