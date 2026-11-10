import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from ..rag.embedder import Embedder
from ..rag.evaluate import evaluate as eval_retrieval
from ..rag.store import INDEX_PATH, RAG_DIR, VectorStore
from .gate import check_gate
from .judge import evaluate_rag
from .toolcalls import evaluate_tools
from .tracing import TracedClient


def main() -> int:
    load_dotenv(RAG_DIR.parents[2] / ".env")
    client = TracedClient(anthropic.Anthropic(), tag="eval")
    store, emb = VectorStore.load(INDEX_PATH), Embedder()

    tools = evaluate_tools(client)
    retr = eval_retrieval(store, emb, k=3)
    rag = evaluate_rag(store, emb, client, client)
    s = client.summary()

    metrics = {
        "tool_accuracy": tools["tool_accuracy"],
        "args_accuracy": tools["args_accuracy"],
        "dangerous_calls": tools["dangerous_calls"],
        "hit_rate": retr["hit_rate"],
        "mrr": retr["mrr"],
        "avg_faithfulness": rag["avg_faithfulness"],
        "answer_rate": rag["answer_rate"],
        "refusal_rate": rag["refusal_rate"],
        "judge_errors": rag["judge_errors"],
        "p95_ms": s["p95_ms"],
        "cost_usd": s["cost_usd"],
        "llm_calls": s["calls"],
    }
    failures = check_gate(metrics)
    report = {
        "metrics": metrics,
        "failures": failures,
        "tool_misses": tools["misses"],
        "retrieval_misses": retr["misses"],
    }
    Path("eval_report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    print("GATE:", "PASS" if not failures else "FAIL")
    for f in failures:
        print("  -", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())