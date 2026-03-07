# Multi-LLM Orchestration Platform — Backend

A FastAPI backend that intelligently routes AI prompts across multiple LLM providers using configurable scoring strategies. Designed to eliminate vendor lock-in, reduce cost, and maintain uptime through automatic failover.

## Architecture

```
Request → main.py (FastAPI) → router.py (RoutingEngine) → providers/
                                    ↓
                         Score all available providers
                         Select winner by strategy
                         Call provider, fallback on failure
                                    ↓
                         Return response + routing metadata
```

## Project Structure

```
multi-llm-backend/
├── main.py                    # FastAPI app, all endpoints
├── router.py                  # Core routing engine (the interesting part)
├── models.py                  # Pydantic request/response schemas
├── requirements.txt
└── providers/
    ├── test_router.py
    ├── base.py                # Abstract base + ProviderStats + circuit breaker
    ├── openai_provider.py     # Real OpenAI GPT-4o-mini integration
    └── mock_providers.py      # Simulated Anthropic + Gemini (realistic latency/failures)
```

## Routing Strategies

|Strategy     |Logic                                                   |
|-------------|--------------------------------------------------------|
|`balanced`   |Weighted score: 45% cost + 35% latency + 20% reliability|
|`cheapest`   |Always route to lowest cost-per-token provider          |
|`fastest`    |Always route to lowest average latency provider         |
|`round_robin`|Distribute evenly across all active providers           |

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...

# Run the server
uvicorn main:app --reload --port 8000
```

## API Endpoints

### `POST /chat`

Route a prompt through the best provider.

```json
{
  "prompt": "Explain transformer attention in one paragraph",
  "strategy": "balanced",
  "max_tokens": 256,
  "fallback_enabled": true
}
```

**Response includes:** content, provider used, routing strategy, latency, cost, and whether a fallback was triggered.

### `GET /metrics`

Platform-wide stats — total requests, cost savings %, avg latency, per-provider breakdown. Consumed by the React dashboard.

### `GET /routing/explain?strategy=balanced`

Dry-run the routing decision. See exactly why the engine would pick a given provider, with scores and alternatives.

### `GET /health`

Live health check across all providers.

### `GET /providers`

Per-provider stats: success rate, avg latency, circuit breaker status.

## Circuit Breaker

Each provider tracks consecutive failures. After 3 consecutive failures, the circuit opens and that provider is excluded from routing for 60 seconds, then automatically retried. This prevents a degraded provider from dragging down overall latency.

## Cost Savings Calculation

The `/metrics` endpoint computes actual savings vs a hypothetical baseline where every request went to the most expensive provider in the pool. This number feeds the “Cost Savings %” card in the React dashboard.

## Connecting to the React Dashboard

Set the React dashboard’s API base URL to `http://localhost:8000` and replace the `setInterval` mock data in the frontend with real `fetch` calls to `/metrics` and `/providers`.

## Environment Variables

```
OPENAI_API_KEY=sk-...       # Required for real OpenAI calls
```

Anthropic and Gemini providers are simulated. To add real integrations, implement `complete()` and `health_check()` in a new file following `openai_provider.py` as the template, then register the provider in `main.py`’s `build_providers()`.