import json
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from .evals.tracing import TracedClient
from . import models
from .auth import get_current_user
from .database import get_db
from .metrics import RATE_LIMITED

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL = "claude-haiku-4-5"
router = APIRouter(prefix="/assistant", tags=["assistant"])

SYSTEM = (
    "Tum FoodOps ke support assistant ho. Order ya restaurant ki info ke liye "
    "hamesha tools use karo, kabhi guess mat karo. Tum sirf is logged-in customer "
    "ke orders dekh sakte ho. Jawab chhota aur Hinglish mein do."
)

TOOLS = [
    {
        "name": "get_order_status",
        "description": "Customer ke apne order ka status batata hai. "
        "Tab use karo jab customer kisi order number ke baare mein poochhe.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "integer", "description": "Order number"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "list_my_recent_orders",
        "description": "Customer ke latest orders ki list. Jab order number nahi pata ho.",
        "input_schema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "1 se 5"}},
        },
    },
    {
        "name": "search_restaurants",
        "description": "Naam ya cuisine se restaurants dhoondhta hai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Restaurant naam ya cuisine"},
                "limit": {"type": "integer", "description": "1 se 5"},
            },
            "required": ["query"],
        },
    },
]


# ---------- Args schemas (NOTE: kisi mein user_id nahi hai) ----------
class OrderArgs(BaseModel):
    order_id: int = Field(gt=0)


class RecentArgs(BaseModel):
    limit: int = Field(default=3, ge=1, le=5)


class SearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=50)
    limit: int = Field(default=3, ge=1, le=5)


def _s(value) -> str:
    """Enum ho ya plain string, dono ko string bana do."""
    return str(getattr(value, "value", value))


def build_tools(db: Session, user) -> dict:
    """Har request ke liye naye tools. user aur db closure mein bandhe hain."""

    def get_order_status(a: OrderArgs) -> dict:
        order = (
            db.query(models.Order)
            .filter(models.Order.id == a.order_id, models.Order.user_id == user.id)
            .first()
        )
        if order is None:  # dusre ka order bhi yahi jawab dega
            return {"error": f"Order {a.order_id} not found"}
        return {"order_id": order.id, "status": _s(order.status)}

    def list_my_recent_orders(a: RecentArgs) -> dict:
        rows = (
            db.query(models.Order)
            .filter(models.Order.user_id == user.id)
            .order_by(models.Order.id.desc())
            .limit(a.limit)
            .all()
        )
        return {"orders": [{"order_id": o.id, "status": _s(o.status)} for o in rows]}

    def search_restaurants(a: SearchArgs) -> dict:
        like = f"%{a.query}%"
        rows = (
            db.query(models.Restaurant)
            .filter(
                models.Restaurant.name.ilike(like) | models.Restaurant.cuisine.ilike(like)
            )
            .limit(a.limit)
            .all()
        )
        return {"results": [{"id": r.id, "name": r.name, "cuisine": r.cuisine} for r in rows]}

    return {
        "get_order_status": (OrderArgs, get_order_status),
        "list_my_recent_orders": (RecentArgs, list_my_recent_orders),
        "search_restaurants": (SearchArgs, search_restaurants),
    }


def run_tool(registry: dict, name: str, raw_input: dict) -> tuple[str, bool]:
    if name not in registry:
        return f"Unknown tool: {name}", True
    args_model, func = registry[name]
    try:
        args = args_model.model_validate(raw_input)
    except ValidationError as e:
        return f"Invalid arguments: {e.errors()[0]['msg']}", True
    try:
        return json.dumps(func(args)), False
    except Exception:
        return "Tool failed", True  # internal detail model/user ko mat do


def run_assistant(message: str, db: Session, user, client, max_steps: int = 5):
    """Return: (reply_text, tools_used)"""
    registry = build_tools(db, user)
    messages: list[dict[str, Any]] = [{"role": "user", "content": message}]
    used: list[str] = []

    for _ in range(max_steps):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=500,
            temperature=0,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text"), used

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                used.append(block.name)
                content, is_err = run_tool(registry, block.name, block.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": content,
                        "is_error": is_err,
                    }
                )
        messages.append({"role": "user", "content": results})

    raise RuntimeError("Assistant loop khatam nahi hua")


# ---------- Rate limit (in-memory, single process; Redis baad mein) ----------
RATE_LIMIT, RATE_WINDOW = 10, 60
_hits: dict[int, deque] = defaultdict(deque)


def check_rate_limit(user_id: int) -> None:
    now = time.monotonic()
    q = _hits[user_id]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        RATE_LIMITED.inc()
        raise HTTPException(status_code=429, detail="Bahut zyada requests, 1 minute baad try karo")
    q.append(now)


# ---------- Endpoint ----------
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    reply: str
    tools_used: list[str]


def get_client():
    return TracedClient(anthropic.Anthropic(), tag="api")  # lazy; tests override karte hain


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    client=Depends(get_client),
):
    check_rate_limit(user.id)
    try:
        reply, used = run_assistant(body.message, db, user, client)
    except anthropic.AnthropicError:
        raise HTTPException(status_code=502, detail="AI service abhi available nahi hai")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Assistant jawab nahi de paya")
    return ChatResponse(reply=reply, tools_used=used)