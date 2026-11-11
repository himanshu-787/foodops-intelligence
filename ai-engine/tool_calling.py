import json
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODEL = "claude-haiku-4-5"

# Abhi fake data. 10.5 mein asli DB se jodenge.
FAKE_ORDERS = {
    42: {"status": "out_for_delivery", "eta_min": 25, "total": 450},
    77: {"status": "delivered", "eta_min": 0, "total": 320},
}
FAKE_RESTAURANTS = [
    {"id": 1, "name": "Biryani House", "cuisine": "biryani", "rating": 4.5},
    {"id": 2, "name": "Pizza Point", "cuisine": "pizza", "rating": 4.2},
    {"id": 3, "name": "Dum Biryani Co", "cuisine": "biryani", "rating": 4.1},
]


# ---------- Args ka schema (validation ke liye) ----------
class OrderStatusArgs(BaseModel):
    order_id: int = Field(gt=0)


class SearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=50)
    limit: int = Field(default=3, ge=1, le=5)


# ---------- Asli functions (read-only) ----------
def get_order_status(args: OrderStatusArgs) -> dict:
    order = FAKE_ORDERS.get(args.order_id)
    if order is None:
        return {"error": f"Order {args.order_id} not found"}
    return {"order_id": args.order_id, **order}


def search_restaurants(args: SearchArgs) -> dict:
    q = args.query.lower()
    hits = [r for r in FAKE_RESTAURANTS if q in r["name"].lower() or q in r["cuisine"]]
    return {"results": hits[: args.limit]}


# Registry: tool name -> (args model, function)
REGISTRY = {
    "get_order_status": (OrderStatusArgs, get_order_status),
    "search_restaurants": (SearchArgs, search_restaurants),
}

# ---------- Claude ko dikhane wala menu card ----------
TOOLS = [
    {
        "name": "get_order_status",
        "description": "Kisi order ka current status aur ETA batata hai. "
        "Tab use karo jab customer apne order ke baare mein poochhe.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "integer", "description": "Order number"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "search_restaurants",
        "description": "Naam ya cuisine se restaurants dhoondhta hai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Restaurant naam ya cuisine"},
                "limit": {"type": "integer", "description": "Max results (1-5)"},
            },
            "required": ["query"],
        },
    },
]

SYSTEM = (
    "Tum FoodOps ke support assistant ho. Order ya restaurant ki info ke liye "
    "hamesha tools use karo, kabhi guess mat karo. Jawab chhota aur Hinglish mein do."
)


def run_tool(name: str, raw_input: dict) -> tuple[str, bool]:
    """Tool chalao. Return: (result_text, is_error). Kabhi crash nahi karta."""
    if name not in REGISTRY:
        return f"Unknown tool: {name}", True
    args_model, func = REGISTRY[name]
    try:
        args = args_model.model_validate(raw_input)
    except ValidationError as e:
        return f"Invalid arguments: {e.errors()[0]['msg']}", True
    try:
        return json.dumps(func(args)), False
    except Exception as e:  # tool ka bug model tak error ban ke jaye, server crash na ho
        return f"Tool failed: {e}", True


def chat_with_tools(user_text: str, client: Any = None, max_steps: int = 5) -> str:
    client = client or anthropic.Anthropic()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]

    for _ in range(max_steps):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        # Assistant ka poora turn (tool_use blocks ke saath) history mein daalo
        messages.append({"role": "assistant", "content": resp.content})

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                content, is_err = run_tool(block.name, block.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": content,
                        "is_error": is_err,
                    }
                )
        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"Tool loop {max_steps} steps mein khatam nahi hua")


if __name__ == "__main__":
    for q in [
        "Mera order 42 kahan hai?",
        "Koi achi biryani wali jagah batao",
        "Order 999 ka status?",
    ]:
        print(q, "\n ->", chat_with_tools(q), "\n")