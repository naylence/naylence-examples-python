# Multi‑Agent Text Analysis Pipeline

This example demonstrates a **distributed multi‑agent pipeline** with Naylence. Multiple agents collaborate to analyze text: one agent summarizes, another evaluates sentiment, and a third orchestrates them and combines results. A client then consumes the aggregated analysis.

```
request: client ──▶ sentinel ──▶ analysis-agent ──┬─▶ summarizer-agent
                                                  └─▶ sentiment-agent
reply:   client ◀─ sentinel ◀─────────────────────┴──────── results merged
```

> ⚠️ **Security note:** This demo is intentionally **insecure** (no TLS, no identities, no overlay encryption). Later examples introduce secure admission, envelope signing, and overlay security.

---

## What you’ll learn

* How to run multiple agents on the same fabric, each with its own logical address.
* How one agent (`AnalysisAgent`) can call others in parallel using **`Agent.broadcast`** (scatter–gather pattern).
* How to structure an orchestrator that merges outputs into a combined payload.

---

## Components

* **sentinel.py** — runs the sentinel (fabric router at `:8000`).
* **summarizer\_agent.py** — uses OpenAI to generate a summary of input text.
* **sentiment\_agent.py** — uses OpenAI to score sentiment 1–5.
* **analysis\_agent.py** — orchestrator; dispatches to summarizer & sentiment agents, collects results, returns combined object.
* **client.py** — submits text to the analysis agent and prints JSON result.
* **common.py** — shared addresses and OpenAI client setup.
* **docker-compose.yml** — runs sentinel + three agents; client runs on host.

**Logical addresses**

* `summarizer@fame.fabric`
* `sentiment@fame.fabric`
* `analysis@fame.fabric`

---

## Quick start (Docker Compose)

1. **Start services**

```bash
docker compose up -d
```

This launches:

* **sentinel** on `localhost:8000`
* **summarizer-agent**, **sentiment-agent**, and **analysis-agent** connected downstream.

2. **Run the client (host)**

```bash
export OPENAI_API_KEY="sk-..."  # ensure set
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

### Example output

```json
{
  "summary": "The film Galactic Frontier dazzles visually but has a predictable plot and shallow characters.",
  "sentiment": "3"
}
```

3. **Stop services**

```bash
docker compose down --remove-orphans
```

---

## Standalone (no Compose)

Run each component in separate terminals:

**Terminal A — sentinel**

```bash
python sentinel.py
```

**Terminal B — summarizer**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python summarizer_agent.py
```

**Terminal C — sentiment**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python sentiment_agent.py
```

**Terminal D — analysis (orchestrator)**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python analysis_agent.py
```

**Terminal E — client**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

---

## Code snippets

### AnalysisAgent orchestration

```python
class AnalysisAgent(BaseAgent):
    async def run_task(self, payload, id):
        result = await Agent.broadcast(
            [SUMMARIZER_AGENT_ADDR, SENTIMENT_AGENT_ADDR],
            payload
        )
        return {
            "summary": result[0][1],
            "sentiment": result[1][1],
        }
```

### Client call

```python
async with FameFabric.create(root_config=dev_mode.CLIENT_CONFIG):
    agent = Agent.remote_by_address(ANALYSIS_AGENT_ADDR)
    result = await agent.run_task(payload=text)
    print(json.dumps(result, indent=2))
```

---

## Troubleshooting

* **Missing API key** → set `OPENAI_API_KEY` in your shell.
* **Agents don’t connect** → start sentinel first; ensure `FAME_DIRECT_ADMISSION_URL` is set.
* **Results empty** → check OpenAI model availability; override with `MODEL_NAME` env var.

---

## Next steps

* Add more specialized agents (e.g., keyword extractor, entity recognizer) and have the analysis agent orchestrate them.
* Chain agents sequentially (e.g., translation → summarization → sentiment).
* Add resilience (timeouts, retries, degraded results if one agent fails).
* Secure the pipeline with authenticated identities and overlay encryption.

---

This example shows how **multiple agents** can collaborate seamlessly in a distributed fabric, with orchestration logic living inside a higher‑level agent rather than the client.
