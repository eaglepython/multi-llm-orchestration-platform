from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class RoutingStrategy(str, Enum):
CHEAPEST = “cheapest”        # Always pick lowest cost
FASTEST = “fastest”          # Always pick lowest latency
BALANCED = “balanced”        # Weighted score: cost + latency + reliability
ROUND_ROBIN = “round_robin”  # Distribute evenly

class ChatRequest(BaseModel):
prompt: str = Field(…, min_length=1, max_length=8000)
strategy: RoutingStrategy = RoutingStrategy.BALANCED
max_tokens: int = Field(default=512, ge=1, le=4096)
preferred_provider: Optional[str] = None  # Override routing if set
fallback_enabled: bool = True              # Allow failover on error

class ChatResponse(BaseModel):
content: str
provider_used: str
model: str
routing_strategy: str
response_time_ms: int
cost_usd: float
tokens_used: int
fallback_triggered: bool = False
fallback_reason: Optional[str] = None

class ProviderHealth(BaseModel):
name: str
status: Literal[“active”, “degraded”, “offline”]
avg_response_time_ms: float
success_rate: float
total_requests: int
total_cost_usd: float
cost_per_1k_tokens: float
last_checked: str

class PlatformMetrics(BaseModel):
total_requests: int
successful_requests: int
failed_requests: int
total_cost_usd: float
avg_response_time_ms: float
cost_savings_pct: float         # vs always using most expensive
providers: list[ProviderHealth]

class RoutingDecision(BaseModel):
selected_provider: str
reason: str
score: float
alternatives_considered: list[dict]