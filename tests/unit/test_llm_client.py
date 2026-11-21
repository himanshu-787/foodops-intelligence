from types import SimpleNamespace

from app.llm_client import (
    from_groq_response,
    to_groq_messages,
    to_groq_tools,
)


def test_to_groq_tools_converts_anthropic_schema():
    anthropic_tools = [
        {
            "name": "lookup_order",
            "description": "Find an order",
            "input_schema": {
                "type": "object",
                "properties": {"order_id": {"type": "integer"}},
                "required": ["order_id"],
            },
        }
    ]
    groq_tools = to_groq_tools(anthropic_tools)
    assert len(groq_tools) == 1
    assert groq_tools[0]["type"] == "function"
    assert groq_tools[0]["function"]["name"] == "lookup_order"
    assert "parameters" in groq_tools[0]["function"]


def test_to_groq_messages_with_system_and_blocks():
    messages = [
        {"role": "user", "content": "hello"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "checking"},
                {"type": "tool_use", "id": "t1", "name": "lookup", "input": {"id": 10}},
            ],
        },
        {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "found"}],
        },
    ]
    out = to_groq_messages(messages, system="Be helpful")
    assert out[0] == {"role": "system", "content": "Be helpful"}
    assert out[1] == {"role": "user", "content": "hello"}
    assert out[2]["role"] == "assistant"
    assert out[2]["tool_calls"][0]["id"] == "t1"
    assert out[3] == {"role": "tool", "tool_call_id": "t1", "content": "found"}


def test_from_groq_response_parses_content_and_tools():
    fake_completion = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="done",
                    tool_calls=[
                        SimpleNamespace(
                            id="call_99",
                            function=SimpleNamespace(
                                name="check", arguments='{"item": "pizza"}'
                            ),
                        )
                    ],
                )
            )
        ],
        usage=SimpleNamespace(prompt_tokens=15, completion_tokens=8),
    )
    res = from_groq_response(fake_completion)
    assert res.stop_reason == "tool_use"
    assert len(res.content) == 2
    assert res.content[0].type == "text" and res.content[0].text == "done"
    assert res.content[1].type == "tool_use" and res.content[1].name == "check"
    assert res.content[1].input == {"item": "pizza"}
    assert res.usage.input_tokens == 15
    assert res.usage.output_tokens == 8
