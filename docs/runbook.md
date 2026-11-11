# FoodOps Runbook

Har alert ka naam yahan ek `##` heading hai. Alert aaye toh seedha us section par jao.

## BackendDown
- `docker compose ps` / platform dashboard: container chal raha hai?
- Logs dekho (JSON, `level=ERROR`). Last deploy ke baad shuru hua? Pichhla SHA tag wapas lagao.
- `/ready` check karo: DB down toh backend uth ke bhi 503 dega.

## HighErrorRate
- Grafana "5xx error ratio" dekho, kaunsa `path` zyada fail ho raha hai.
- Wahi `path` ke logs mein `request_id` dhoondho, ek failing request ko poora follow karo.
- `foodops_llm_calls_total{outcome="error"}` bhi badh raha hai? Toh LLMErrorsHigh wala section dekho.

## HighLatencyP95
- Dekho slow `path` kaunsa hai, aur `foodops_llm_call_seconds` bhi slow hai ya nahi.
- LLM slow hai toh Anthropic status dekho. LLM theek hai toh DB query ya CPU.

## LLMErrorsHigh
- Logs mein error type dekho (auth, rate limit, overloaded, timeout).
- Auth error: `ANTHROPIC_API_KEY` galat ya expire. Key badlo aur restart karo.
- Provider outage: users ko 502 mil raha hai (expected). Status page dekho, intezaar.

## LLMCostSpike
- `foodops_llm_tokens_total` by `direction`: input ya output badha?
- `foodops_rate_limited_total` aur `/agent/chat` ya `/rag/ask` ka request rate dekho, koi abuse?
- Gap: abhi AI endpoints band karne ka koi flag nahi hai. Aakhri raasta `ANTHROPIC_API_KEY` rotate karna hai.

## RagNoAnswerHigh
- `foodops_rag_top_score` ka distribution khisak gaya? Users ke sawal badle ya index purana/missing hai?
- `/ready` mein `rag_index` true hai? `python -m app.rag.build_index` dobara chalao.
- Golden set par `python -m app.rag.evaluate` chalao.
