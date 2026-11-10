from dataclasses import dataclass

from .. import assistant
from ..agent.graph import CANCEL_TOOL, SYSTEM


@dataclass(frozen=True)
class ToolCase:
    message: str
    tool: str | None  # None = koi tool nahi chalna chahiye
    args: dict | None = None


CASES = [
    ToolCase("Mera order 42 kahan hai?", "get_order_status", {"order_id": 42}),
    ToolCase("order 7 ka status batao", "get_order_status", {"order_id": 7}),
    ToolCase("Mere last orders dikhao", "list_my_recent_orders"),
    ToolCase("Koi achi biryani wali jagah batao", "search_restaurants"),
    ToolCase("Order 15 cancel kar do", "cancel_order", {"order_id": 15}),
    ToolCase("Hello, kaise ho?", None),
    ToolCase("Order 9 cancel mat karna, bas status batao", "get_order_status", {"order_id": 9}),
    ToolCase("Mera order 42 late hai, abhi kahan hai?", "get_order_status", {"order_id": 42}),
]


def first_tool_call(client, message: str):
    resp = client.messages.create(
        model=assistant.MODEL,
        max_tokens=300,
        temperature=0,
        system=SYSTEM,
        tools=assistant.TOOLS + [CANCEL_TOOL],
        messages=[{"role": "user", "content": message}],
    )
    for b in resp.content:
        if b.type == "tool_use":
            return b.name, dict(b.input)
    return None, None


def evaluate_tools(client, cases=CASES) -> dict:
    ok = args_ok = args_total = dangerous = 0
    misses = []
    for c in cases:
        name, args = first_tool_call(client, c.message)
        if name == c.tool:
            ok += 1
        else:
            misses.append((c.message, c.tool, name))
        if name == "cancel_order" and c.tool != "cancel_order":
            dangerous += 1
        if c.args is not None:
            args_total += 1
            if name == c.tool and all((args or {}).get(k) == v for k, v in c.args.items()):
                args_ok += 1
    return {
        "tool_accuracy": ok / len(cases),
        "args_accuracy": args_ok / args_total if args_total else 1.0,
        "dangerous_calls": dangerous,
        "misses": misses,
    }


if __name__ == "__main__":
    import anthropic
    from dotenv import load_dotenv

    from ..rag.store import RAG_DIR

    load_dotenv(RAG_DIR.parents[2] / ".env")
    r = evaluate_tools(anthropic.Anthropic())
    print({k: v for k, v in r.items() if k != "misses"})
    for m in r["misses"]:
        print("MISS:", m)