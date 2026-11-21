import json
import os
from types import SimpleNamespace
from typing import Any


def to_groq_tools(tools: list[dict] | None) -> list[dict] | None:
    if not tools:
        return None
    groq_tools = []
    for t in tools:
        if "input_schema" in t:
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t["input_schema"],
                },
            })
        elif "function" in t:
            groq_tools.append(t)
        else:
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": t.get("name", ""),
                    "description": t.get("description", ""),
                    "parameters": t.get("parameters", {}),
                },
            })
    return groq_tools


def _get_field(obj: Any, field: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


def to_groq_messages(messages: list[dict], system: str | None = None) -> list[dict]:
    groq_msgs: list[dict] = []
    if system:
        groq_msgs.append({"role": "system", "content": system})

    for m in messages:
        role = _get_field(m, "role")
        content = _get_field(m, "content")

        if isinstance(content, str):
            groq_msgs.append({"role": role, "content": content})
        elif isinstance(content, list):
            text_parts = []
            tool_calls = []
            for b in content:
                b_type = _get_field(b, "type")
                if b_type == "text":
                    text_parts.append(_get_field(b, "text", ""))
                elif b_type == "tool_use":
                    inp = _get_field(b, "input", {})
                    tool_calls.append({
                        "id": str(_get_field(b, "id", "call_1")),
                        "type": "function",
                        "function": {
                            "name": _get_field(b, "name", ""),
                            "arguments": json.dumps(inp) if isinstance(inp, dict) else str(inp),
                        },
                    })
                elif b_type == "tool_result":
                    groq_msgs.append({
                        "role": "tool",
                        "tool_call_id": str(_get_field(b, "tool_use_id", "call_1")),
                        "content": str(_get_field(b, "content", "")),
                    })

            if role == "assistant":
                msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": "\n".join(text_parts) if text_parts else None,
                }
                if tool_calls:
                    msg["tool_calls"] = tool_calls
                groq_msgs.append(msg)
            elif role == "user" and text_parts:
                groq_msgs.append({"role": "user", "content": "\n".join(text_parts)})
    return groq_msgs


def from_groq_response(completion: Any) -> SimpleNamespace:
    choice = completion.choices[0]
    message = choice.message
    content_blocks = []

    if message.content:
        content_blocks.append(SimpleNamespace(type="text", text=message.content))

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        for tc in tool_calls:
            args_str = getattr(tc.function, "arguments", "{}")
            try:
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
            except Exception:
                args = {}
            content_blocks.append(SimpleNamespace(
                type="tool_use",
                id=tc.id,
                name=tc.function.name,
                input=args,
            ))

    stop_reason = "tool_use" if tool_calls else "end_turn"
    usage_obj = getattr(completion, "usage", None)
    usage = SimpleNamespace(
        input_tokens=getattr(usage_obj, "prompt_tokens", 0) if usage_obj else 0,
        output_tokens=getattr(usage_obj, "completion_tokens", 0) if usage_obj else 0,
    )
    return SimpleNamespace(
        content=content_blocks,
        stop_reason=stop_reason,
        usage=usage,
    )


class GroqAdapter:
    """Wraps groq.Groq to conform to Anthropic client.messages.create interface."""

    def __init__(self, api_key: str | None = None):
        import groq

        self.client = groq.Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.messages = self

    def create(self, **kwargs) -> SimpleNamespace:
        raw_model = kwargs.get("model", "llama-3.1-8b-instant")
        if "claude" in raw_model:
            if "sonnet" in raw_model:
                model = os.getenv("GROQ_JUDGE_MODEL", "llama-3.3-70b-versatile")
            else:
                model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        else:
            model = raw_model

        system = kwargs.get("system")
        messages = kwargs.get("messages", [])
        tools = kwargs.get("tools")
        max_tokens = kwargs.get("max_tokens", 500)
        temperature = kwargs.get("temperature", 0)

        groq_msgs = to_groq_messages(messages, system)
        groq_tools = to_groq_tools(tools)

        req: dict[str, Any] = {
            "model": model,
            "messages": groq_msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if groq_tools:
            req["tools"] = groq_tools
            req["tool_choice"] = "auto"

        completion = self.client.chat.completions.create(**req)
        return from_groq_response(completion)


def get_default_llm_client(tag: str = "api"):
    from .evals.tracing import TracedClient

    if os.getenv("GROQ_API_KEY"):
        return TracedClient(GroqAdapter(), tag=tag)
    elif os.getenv("ANTHROPIC_API_KEY"):
        import anthropic

        return TracedClient(anthropic.Anthropic(), tag=tag)
    else:
        # Fallback to Groq if installed, else Anthropic
        try:
            return TracedClient(GroqAdapter(), tag=tag)
        except Exception:
            import anthropic

            return TracedClient(anthropic.Anthropic(), tag=tag)
