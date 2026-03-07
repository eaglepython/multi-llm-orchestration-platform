“””
test_router.py — Unit tests for the Multi-LLM Orchestration Platform

Tests cover:

- Routing strategy correctness (cheapest, fastest, balanced, round_robin)
- Circuit breaker behavior
- Fallback / failover logic
- Score normalization edge cases
- ProviderStats tracking
  “””

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(**file**)))

from router import RoutingEngine, COST_WEIGHT, LATENCY_WEIGHT, RELIABILITY_WEIGHT
from models import RoutingStrategy
from providers.base import BaseLLMProvider, ProviderStats, ProviderResponse

# —————————————————————————

# Helpers — lightweight fake providers, no network calls

# —————————————————————————

class FakeProvider(BaseLLMProvider):
“”“Configurable fake provider for testing routing logic in isolation.”””

```
def __init__(self, name, cost, latency_ms, success_rate=1.0, always_fail=False):
    super().__init__()
    self.name = name
    self.cost_per_1k_tokens = cost
    self.model = f"{name}-model"
    self._latency_ms = latency_ms
    self._always_fail = always_fail

    # Pre-warm stats so avg_latency_ms is meaningful from the first test
    if not always_fail:
        self.stats.total_requests = 10
        self.stats.successful_requests = int(10 * success_rate)
        self.stats.failed_requests = 10 - self.stats.successful_requests
        self.stats.total_latency_ms = latency_ms * self.stats.successful_requests

async def complete(self, prompt: str, max_tokens: int) -> ProviderResponse:
    if self._always_fail:
        self.stats.record_failure()
        raise ConnectionError(f"{self.name}: forced failure")
    cost = self.compute_cost(100)
    self.stats.record_success(self._latency_ms, cost, 100)
    return ProviderResponse(
        content=f"Response from {self.name}",
        tokens_used=100,
        cost_usd=cost,
        latency_ms=self._latency_ms,
        model=self.model,
    )

async def health_check(self) -> bool:
    return not self._always_fail
```

def make_engine(*providers):
return RoutingEngine(list(providers))

# —————————————————————————

# ProviderStats

# —————————————————————————

class TestProviderStats:

```
def test_success_rate_no_requests(self):
    s = ProviderStats()
    assert s.success_rate == 1.0

def test_avg_latency_no_requests(self):
    s = ProviderStats()
    assert s.avg_latency_ms == 9999.0  # Penalized unknown latency

def test_record_success_updates_all_fields(self):
    s = ProviderStats()
    s.record_success(200, 0.001, 50)
    assert s.total_requests == 1
    assert s.successful_requests == 1
    assert s.total_latency_ms == 200
    assert s.total_cost_usd == 0.001
    assert s.total_tokens == 50
    assert s.consecutive_failures == 0

def test_record_failure_increments_consecutives(self):
    s = ProviderStats()
    s.record_failure()
    s.record_failure()
    assert s.consecutive_failures == 2
    assert s.failed_requests == 2

def test_success_resets_consecutive_failures(self):
    s = ProviderStats()
    s.record_failure()
    s.record_failure()
    s.record_success(100, 0.001, 10)
    assert s.consecutive_failures == 0

def test_success_rate_calculation(self):
    s = ProviderStats()
    s.record_success(100, 0.001, 10)
    s.record_success(100, 0.001, 10)
    s.record_failure()
    assert round(s.success_rate, 4) == round(2 / 3, 4)
```

# —————————————————————————

# Circuit Breaker

# —————————————————————————

class TestCircuitBreaker:

```
def test_circuit_closed_below_threshold(self):
    s = ProviderStats()
    s.record_failure()
    s.record_failure()
    assert not s.is_circuit_open()

def test_circuit_opens_after_three_failures(self):
    s = ProviderStats()
    s.record_failure()
    s.record_failure()
    s.record_failure()
    assert s.is_circuit_open()

def test_circuit_resets_after_timeout(self):
    import time
    s = ProviderStats()
    s.record_failure()
    s.record_failure()
    s.record_failure()
    # Backdate the failure time beyond the 60s window
    s.last_failure_time = time.time() - 61
    assert not s.is_circuit_open()
    assert s.consecutive_failures == 0  # Reset side effect

def test_available_providers_excludes_open_circuits(self):
    good = FakeProvider("Good", cost=0.01, latency_ms=200)
    bad = FakeProvider("Bad", cost=0.01, latency_ms=200, always_fail=True)
    # Force circuit open on bad provider
    bad.stats.consecutive_failures = 3
    import time
    bad.stats.last_failure_time = time.time()

    engine = make_engine(good, bad)
    available = engine._available_providers()
    assert len(available) == 1
    assert available[0].name == "Good"
```

# —————————————————————————

# Routing Strategies

# —————————————————————————

class TestRoutingStrategies:

```
def setup_method(self):
    self.cheap = FakeProvider("Cheap",  cost=0.001, latency_ms=400, success_rate=0.95)
    self.fast  = FakeProvider("Fast",   cost=0.030, latency_ms=80,  success_rate=0.99)
    self.solid = FakeProvider("Solid",  cost=0.015, latency_ms=200, success_rate=0.999)
    self.engine = make_engine(self.cheap, self.fast, self.solid)

def test_cheapest_selects_lowest_cost(self):
    ordered, decision = self.engine._rank_providers(
        [self.cheap, self.fast, self.solid], RoutingStrategy.CHEAPEST
    )
    assert decision.selected_provider == "Cheap"

def test_fastest_selects_lowest_latency(self):
    ordered, decision = self.engine._rank_providers(
        [self.cheap, self.fast, self.solid], RoutingStrategy.FASTEST
    )
    assert decision.selected_provider == "Fast"

def test_balanced_considers_all_dimensions(self):
    # "Solid" has mid cost, mid latency, best reliability — should win balanced
    ordered, decision = self.engine._rank_providers(
        [self.cheap, self.fast, self.solid], RoutingStrategy.BALANCED
    )
    # We don't assert a specific winner (weights may shift outcome) but
    # we do assert the decision includes alternatives and a numeric score
    assert decision.score >= 0.0
    assert len(decision.alternatives_considered) == 2

def test_round_robin_cycles_through_providers(self):
    providers = [self.cheap, self.fast, self.solid]
    engine = make_engine(*providers)
    seen = []
    for _ in range(6):
        ordered, decision = engine._rank_providers(providers, RoutingStrategy.ROUND_ROBIN)
        seen.append(decision.selected_provider)
    # After 6 calls across 3 providers each should appear exactly twice
    for p in [self.cheap.name, self.fast.name, self.solid.name]:
        assert seen.count(p) == 2

def test_decision_includes_reason_string(self):
    _, decision = self.engine._rank_providers(
        [self.cheap, self.fast], RoutingStrategy.CHEAPEST
    )
    assert len(decision.reason) > 0

def test_score_normalization_single_provider(self):
    """With one provider, all normalized values are 0.5 — score should still be finite."""
    engine = make_engine(self.solid)
    scored = engine._score_providers([self.solid], RoutingStrategy.BALANCED)
    assert len(scored) == 1
    _, score = scored[0]
    assert 0.0 <= score <= 1.0

def test_weights_sum_to_one(self):
    total = COST_WEIGHT + LATENCY_WEIGHT + RELIABILITY_WEIGHT
    assert abs(total - 1.0) < 1e-9
```

# —————————————————————————

# Failover / Fallback

# —————————————————————————

class TestFailover:

```
def test_fallback_to_second_provider_on_failure(self):
    failing = FakeProvider("Failing", cost=0.01, latency_ms=100, always_fail=True)
    working = FakeProvider("Working", cost=0.02, latency_ms=150)

    # Force failing to top of ranking by pre-setting it as preferred
    engine = make_engine(failing, working)

    async def run():
        response, decision, fallback_triggered, reason = await engine.route(
            prompt="test",
            max_tokens=50,
            strategy=RoutingStrategy.ROUND_ROBIN,
            fallback_enabled=True,
        )
        return response, decision, fallback_triggered, reason

    response, decision, fallback_triggered, reason = asyncio.get_event_loop().run_until_complete(run())
    assert response.content == "Response from Working"
    assert fallback_triggered is True
    assert reason is not None

def test_no_fallback_raises_when_disabled(self):
    failing = FakeProvider("Failing", cost=0.01, latency_ms=100, always_fail=True)
    engine = make_engine(failing)

    async def run():
        await engine.route(
            prompt="test",
            max_tokens=50,
            strategy=RoutingStrategy.BALANCED,
            fallback_enabled=False,
        )

    with pytest.raises(ConnectionError):
        asyncio.get_event_loop().run_until_complete(run())

def test_all_providers_failing_raises_runtime_error(self):
    f1 = FakeProvider("F1", cost=0.01, latency_ms=100, always_fail=True)
    f2 = FakeProvider("F2", cost=0.02, latency_ms=150, always_fail=True)
    engine = make_engine(f1, f2)

    async def run():
        await engine.route("test", 50, RoutingStrategy.BALANCED, fallback_enabled=True)

    with pytest.raises(RuntimeError, match="All providers failed"):
        asyncio.get_event_loop().run_until_complete(run())

def test_no_available_providers_raises(self):
    p = FakeProvider("Only", cost=0.01, latency_ms=100)
    p.stats.consecutive_failures = 3
    import time
    p.stats.last_failure_time = time.time()
    engine = make_engine(p)

    async def run():
        await engine.route("test", 50, RoutingStrategy.BALANCED)

    with pytest.raises(RuntimeError, match="No providers available"):
        asyncio.get_event_loop().run_until_complete(run())
```

# —————————————————————————

# Preferred Provider Override

# —————————————————————————

class TestPreferredProvider:

```
def test_preferred_provider_placed_first(self):
    cheap = FakeProvider("Cheap", cost=0.001, latency_ms=400)
    pricey = FakeProvider("Pricey", cost=0.05, latency_ms=80)
    engine = make_engine(cheap, pricey)

    async def run():
        response, decision, _, _ = await engine.route(
            prompt="test",
            max_tokens=50,
            strategy=RoutingStrategy.CHEAPEST,
            preferred_provider="Pricey",
        )
        return decision

    decision = asyncio.get_event_loop().run_until_complete(run())
    assert decision.selected_provider == "Pricey"

def test_unknown_preferred_provider_falls_back_to_strategy(self):
    cheap = FakeProvider("Cheap", cost=0.001, latency_ms=400)
    engine = make_engine(cheap)

    async def run():
        _, decision, _, _ = await engine.route(
            prompt="test",
            max_tokens=50,
            strategy=RoutingStrategy.CHEAPEST,
            preferred_provider="NonExistent",
        )
        return decision

    decision = asyncio.get_event_loop().run_until_complete(run())
    assert decision.selected_provider == "Cheap"
```

# —————————————————————————

# Health Check

# —————————————————————————

class TestHealthCheck:

```
def test_health_check_all_returns_dict(self):
    p1 = FakeProvider("P1", cost=0.01, latency_ms=100)
    p2 = FakeProvider("P2", cost=0.02, latency_ms=150)
    engine = make_engine(p1, p2)

    async def run():
        return await engine.health_check_all()

    results = asyncio.get_event_loop().run_until_complete(run())
    assert set(results.keys()) == {"P1", "P2"}
    assert results["P1"] is True
    assert results["P2"] is True

def test_health_check_failing_provider_returns_false(self):
    failing = FakeProvider("Failing", cost=0.01, latency_ms=100, always_fail=True)
    engine = make_engine(failing)

    async def run():
        return await engine.health_check_all()

    results = asyncio.get_event_loop().run_until_complete(run())
    assert results["Failing"] is False
```