import hmac
import os
import time

from fastapi import APIRouter, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# ---------- HTTP ----------
HTTP_REQUESTS = Counter(
    "foodops_http_requests_total", "HTTP requests", ["method", "path", "status"]
)
HTTP_LATENCY = Histogram(
    "foodops_http_request_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
IN_FLIGHT = Gauge("foodops_http_in_flight", "Requests abhi process ho rahi hain")


def path_label(request: Request) -> str:
    """Route template (/orders/{order_id}); match na ho toh 'unmatched'. Raw URL kabhi nahi."""
    route = request.scope.get("route")
    return getattr(route, "path", "unmatched")


async def metrics_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
    IN_FLIGHT.inc()
    t0 = time.perf_counter()
    status = 500  # exception upar tak gayi toh yahi record hoga
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        IN_FLIGHT.dec()
        path = path_label(request)
        HTTP_REQUESTS.labels(request.method, path, str(status)).inc()
        HTTP_LATENCY.labels(request.method, path).observe(time.perf_counter() - t0)


# ---------- LLM ----------
LLM_CALLS = Counter("foodops_llm_calls_total", "LLM calls", ["tag", "model", "outcome"])
LLM_TOKENS = Counter("foodops_llm_tokens_total", "LLM tokens", ["model", "direction"])
LLM_COST = Counter("foodops_llm_cost_usd_total", "Estimated LLM cost (USD)", ["model"])
LLM_LATENCY = Histogram(
    "foodops_llm_call_seconds",
    "LLM call latency",
    ["model"],
    buckets=(0.25, 0.5, 1, 2, 4, 8, 16),
)

# ---------- Business ----------
RAG_ANSWERS = Counter("foodops_rag_answers_total", "RAG answers", ["outcome"])
RAG_TOP_SCORE = Histogram(
    "foodops_rag_top_score",
    "Top retrieval score",
    buckets=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
)
AGENT_ACTIONS = Counter(
    "foodops_agent_actions_total", "Agent write actions", ["action", "result"]
)
RATE_LIMITED = Counter("foodops_rate_limited_total", "Rate limit hits")


# ---------- /metrics endpoint ----------
router = APIRouter(tags=["ops"])


@router.get("/metrics", include_in_schema=False)
def metrics(request: Request):
    token = os.getenv("METRICS_TOKEN")  # set ho toh Bearer token zaroori
    if token and not hmac.compare_digest(
        request.headers.get("authorization", ""), f"Bearer {token}"
    ):
        raise HTTPException(status_code=401, detail="unauthorized")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
