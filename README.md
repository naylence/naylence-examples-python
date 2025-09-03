# Naylence Examples — Summary README

This repository is a tour of Naylence’s Agent SDK and runtime patterns, from "hello world" agents to multi‑agent orchestration and enterprise‑grade security. Use it as a workbook: run each example, skim its code, and move to the next.

---

## Directory map

```
examples/
  simple/                 # single‑process, zero‑config building blocks
  distributed/            # hello → RPC → cancellable tasks → multi‑agent pipeline
    hello/
    hello-with-sentinel/
    rpc/
    cancellable/
    multi-agent/
  llm/                    # single‑process LLM + image gen agents
  security/               # admission, overlay signing, sealed channels, SVIDs
    gated/
    overlay/
    advanced/
```

**Conventions**

* Each folder has a short `README.md`, `Makefile` with `start/run/stop`, and minimal code.
* Docker Compose brings up long‑running services (sentinel/agents). Clients usually run from your host with `make run`.
* Env vars like `FAME_DIRECT_ADMISSION_URL` and `OPENAI_API_KEY` are used where relevant.

---

## Recommended learning path

1. **Start tiny — \*\*\*\*`examples/simple/`**
   Learn the core Agent APIs without networking or a sentinel:

   * wrap a function as an agent (`function_as_agent.py`)
   * one‑shot `run_task` vs background tasks (`agent_with_bg_task.py`)
   * basic RPC patterns (`rpc_agent.py`)
   * echo / ping‑pong for round‑trip mental model

2. **Single‑process with models — \*\*\*\*`examples/llm/`**
   Use the same Agent APIs to call external LLMs:

   * Q\&A function‑agent (`llm_agent.py`)
   * Chat agent with per‑session memory (`chat_agent.py`)
   * Image generation agent with a tiny viewer (`image_generation_agent.py`, `view_images.py`)

   *Goal:* see that “agent” is a programming model first; distribution is optional.

3. **Introduce the fabric — \*\*\*\*`examples/distributed/hello/`**
   Run a **sentinel** and a separate **agent** container; call the agent from a host client. Learn the admission URL and the idea of logical addresses (`echo@fame.fabric`).

4. **RPC on the fabric — \*\*\*\*`examples/distributed/rpc/`**
   Expose operations with `@operation`, including **streaming** (e.g., Fibonacci stream). Call methods over the fabric like local methods.

5. **Long‑running + cancellation — \*\*\*\*`examples/distributed/cancellable/`**
   Use **A2A task APIs**: start a background task, subscribe to **status/artifact** updates, cancel mid‑flight.

6. **Multi‑agent orchestration — \*\*\*\*`examples/distributed/multi-agent/`**
   Launch multiple agents and orchestrate them with **scatter–gather** (`Agent.broadcast`). Example: summarizer + sentiment + aggregator.

7. **Security tiers — \*\*\*\*`examples/security/`**
   Progressively add real‑world security:

   * **gated/**: OAuth2‑gated admission to the sentinel
   * **overlay/**: signed envelopes (provenance, non‑repudiation)
   * **advanced/**: strict overlay + admission + SPIFFE/X.509 (SVID) identities and sealed channels (BSL add‑on)

> Tip: You can stop at any stage that fits your needs. If you just need distributed RPC today, you can live in `distributed/rpc` and return for security later.

---

## Quick prerequisites

* **Python 3.12+** if you run scripts locally
* **Docker + Docker Compose** for anything in `distributed/` or `security/`
* **OpenAI API key** for `llm/` and any LLM‑backed pipelines: `export OPENAI_API_KEY=…`

---

## How to run (common pattern)

Most distributed examples:

```bash
make start       # brings up sentinel + agent(s)
make run         # runs the client from your host
make run-verbose # prints envelope traffic for learning/debugging
make stop        # tears down containers
```

If you prefer not to use `make`, see each folder’s `docker-compose.yml` and `README.md` for equivalent commands.

---

## Example catalog (high‑level)

### `simple/`

* **function\_as\_agent.py** — wrap a plain async function as an agent
* **echo\_agent.py** — minimal one‑shot `run_task`
* **agent\_with\_bg\_task.py** — start/subscribe/cancel lifecycle
* **rpc\_agent.py** — define method‑style RPC with `@operation`
* **agent\_ping\_pong.py**\*\*`, `\*\***a2a\_agent.py\`** — tiny messaging exercises

### `llm/`

* **llm\_agent.py** — function‑agent does Q\&A with GPT
* **chat\_agent.py** — chat with per‑session memory (REPL)
* **image\_generation\_agent.py** — DALL‑E image gen; saves PNGs; optional local viewer

### `distributed/`

* **hello/** — echo across a real fabric (sentinel + agent)
* **hello-with-sentinel/** — same idea with explicit sentinel config
* **rpc/** — math agent with add/multiply + streaming Fibonacci
* **cancellable/** — background task with progress artifacts; client cancels at threshold
* **multi-agent/** — summarizer + sentiment + aggregator; `Agent.broadcast` scatter–gather

### `security/` (progressive)

* **gated/** — OAuth2 token‑gated admission; TLS via Caddy as reverse proxy
* **overlay/** — overlay signing (provenance, tamper‑evidence) on messages
* **advanced/** — strict overlay + admission + CA‑issued SVIDs (SPIFFE/X.509); sealed channels

---

## What to learn in each stage

* **Agent model**: `BaseAgent`, `Agent.from_handler`, `run_task` vs `start_task`, artifacts and streams
* **Fabric mental model**: logical addresses, the sentinel as attach point, admission URL
* **RPC ergonomics**: `@operation` methods, request/response vs streaming
* **A2A tasks**: progress artifacts, status updates, cancellation
* **Orchestration**: parallel fan‑out and result merging
* **Security**: OAuth2 tokens (gated), overlay signing (integrity/provenance), sealed channels + SVIDs (advanced)

---

## Troubleshooting quickies

* **Client can’t connect** → ensure `FAME_DIRECT_ADMISSION_URL` points to the sentinel (`ws://localhost:8000/...` from host; `ws://sentinel:8000/...` inside Compose).
* **No LLM output** → set `OPENAI_API_KEY`; verify model availability or override model via `MODEL_NAME` when supported.
* **Agents don’t attach** → start the sentinel first; check env files in `security/*/config/`.
* **Port 8000/443 in use** → change the Compose port mapping or free the port.

---

## Where to go next

* Extend the math RPC with your own operations (including streaming)
* Add more micro‑agents (keyword extractor, NER, RAG) to the multi‑agent pipeline
* Turn on overlay signing in non‑security examples to compare envelope metadata
* Swap OAuth dev server with your IdP; integrate your own CA for SVID issuance

---

Happy hacking! If you spot a rough edge, file an issue with the example name and any logs/commands you ran.
