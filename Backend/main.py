“””
main.py — Multi-LLM Orchestration Platform API

## Endpoints

POST /chat            — Route a prompt through the best available LLM
GET  /metrics         — Platform-wide stats (feeds the React dashboard)
GET  /providers       — Per-provider health and performance
GET  /health          — Live health check across all providers
GET  /routing/explain — Dry-run: show which provider would be chosen and why
“””

import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
ChatRequest,
ChatResponse,
PlatformMetrics,
ProviderHealth,
RoutingStrategy,
)
from router import RoutingEngine
from providers import OpenAIProvider, AnthropicProvider, GeminiProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

# —————————————————————————

# Provider registry — add or remove providers here, nothing else changes

# —————————————————————————

def build_providers():
providers = []

```
# Real provider (requires OPENAI_API_KEY in environment)
try:
    providers.append(OpenAIProvider())
    logger.info("OpenAI provider loaded")
except ValueError as e:
    logger.warning(f"OpenAI skipped: {e}")

# Simulated providers — always available for routing comparison
providers.append(AnthropicProvider())
providers.append(GeminiProvider())

if not providers:
    raise RuntimeError("No providers configured. Set OPENAI_API_KEY.")

return providers
```

engine: RoutingEngine = None  # initialized at startup

@asynccontextmanager
async def lifespan(app: FastAPI):
global engine
providers = build_providers()
engine = RoutingEngine(providers)
logger.info(f”Routing engine started with {len(providers)} providers”)
yield
logger.info(“Shutdown complete”)

app = FastAPI(
title=“Multi-LLM Orchestration Platform”,
description=“Intelligent AI provider routing with cost optimization and failover”,
version=“1.0.0”,
lifespan=lifespan,
)

app.add_middleware(
CORSMiddleware,
allow_origins=[”*”],  # Tighten in production
allow_methods=[”*”],
allow_headers=[”*”],
)

# —————————————————————————

# Routes

# —————————————————————————

@app.post(”/chat”, response_model=ChatResponse)
async def chat(request: ChatRequest):
“””
Route a prompt to the best available LLM based on the chosen strategy.
Returns the response along with routing metadata for observability.
“””
if engine is None:
raise HTTPException(503, “Routing engine not ready”)

```
try:
    response, decision, fallback_triggered, fallback_reason = await engine.route(
        prompt=request.prompt,
        max_tokens=request.max_tokens,
        strategy=request.strategy,
        preferred_provider=request.preferred_provider,
        fallback_enabled=request.fallback_enabled,
    )
except RuntimeError as e:
    raise HTTPException(503, str(e))

return ChatResponse(
    content=response.content,
    provider_used=decision.selected_provider,
    model=response.model,
    routing_strategy=request.strategy.value,
    response_time_ms=response.latency_ms,
    cost_usd=round(response.cost_usd, 6),
    tokens_used=response.tokens_used,
    fallback_triggered=fallback_triggered,
    fallback_reason=fallback_reason,
)
```

@app.get(”/metrics”, response_model=PlatformMetrics)
async def get_metrics():
“”“Aggregate stats across all providers — consumed by the React dashboard.”””
providers = engine.providers
provider_healths = []
total_requests = total_success = total_failed = 0
total_cost = total_latency = 0.0

```
# Baseline: cost if every request went to the most expensive provider
most_expensive = max(p.cost_per_1k_tokens for p in providers)

for p in providers:
    s = p.stats
    total_requests += s.total_requests
    total_success += s.successful_requests
    total_failed += s.failed_requests
    total_cost += s.total_cost_usd
    total_latency += s.total_latency_ms

    status = "offline"
    if not p.stats.is_circuit_open():
        status = "active" if s.success_rate >= 0.97 else "degraded"

    provider_healths.append(ProviderHealth(
        name=p.name,
        status=status,
        avg_response_time_ms=round(s.avg_latency_ms, 1),
        success_rate=round(s.success_rate, 4),
        total_requests=s.total_requests,
        total_cost_usd=round(s.total_cost_usd, 6),
        cost_per_1k_tokens=p.cost_per_1k_tokens,
        last_checked=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    ))

avg_latency = (total_latency / total_success) if total_success > 0 else 0

# Cost savings vs always using most expensive
hypothetical_max_cost = (sum(p.stats.total_tokens for p in providers) / 1000) * most_expensive
savings_pct = 0.0
if hypothetical_max_cost > 0:
    savings_pct = ((hypothetical_max_cost - total_cost) / hypothetical_max_cost) * 100

return PlatformMetrics(
    total_requests=total_requests,
    successful_requests=total_success,
    failed_requests=total_failed,
    total_cost_usd=round(total_cost, 6),
    avg_response_time_ms=round(avg_latency, 1),
    cost_savings_pct=round(savings_pct, 2),
    providers=provider_healths,
)
```

@app.get(”/providers”)
async def get_providers():
“”“Per-provider breakdown for the dashboard provider status cards.”””
return [
{
“name”: p.name,
“model”: getattr(p, “model”, “unknown”),
“cost_per_1k_tokens”: p.cost_per_1k_tokens,
“circuit_open”: p.stats.is_circuit_open(),
“stats”: {
“total_requests”: p.stats.total_requests,
“success_rate”: round(p.stats.success_rate, 4),
“avg_latency_ms”: round(p.stats.avg_latency_ms, 1),
“total_cost_usd”: round(p.stats.total_cost_usd, 6),
“consecutive_failures”: p.stats.consecutive_failures,
},
}
for p in engine.providers
]

@app.get(”/health”)
async def health():
“”“Live health check — hits each provider and reports status.”””
results = await engine.health_check_all()
all_ok = all(results.values())
return {
“status”: “healthy” if all_ok else “degraded”,
“providers”: results,
“timestamp”: time.strftime(”%Y-%m-%dT%H:%M:%SZ”, time.gmtime()),
}

@app.get(”/routing/explain”)
async def explain_routing(
strategy: RoutingStrategy = RoutingStrategy.BALANCED,
preferred_provider: str = None,
):
“””
Dry-run the routing decision without making a real API call.
Useful for understanding why the engine picks a given provider.
“””
available = engine._available_providers()
if not available:
raise HTTPException(503, “No providers available”)

```
_, decision = engine._rank_providers(available, strategy)
return decision
```