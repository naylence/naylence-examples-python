# Naylence Examples

This repository is a tour of Naylence’s Agent SDK and runtime patterns, from "hello world" agents to multi‑agent orchestration and production‑grade security. Use it as a workbook: run each example, skim its code, and move to the next.

---

## Directory map

```
examples/
  simple/                      # single‑process, zero‑config building blocks
  distributed/                 # hello → RPC → cancellable → orchestration → topologies
    hello/
    hello-with-sentinel/
    rpc/
    cancellable/
    multi-agent/
    biomes/
    peers/
    stateful-conversation/
    push-notifications/
    status-subscription/
    capability-routing/
  llm/                         # single‑process LLM + image gen agents
    chat_agent.py
    image_generation_agent.py
    llm_agent.py
  monitoring/
    open-telemetry/
  security/                    # admission, overlay, advanced identities & routing
    gated/
    overlay/
    advanced/
    http-connector/
    stickiness/
```

**Conventions**

* Each folder has a short `README.md`, a `Makefile` with `start/run/stop`, and minimal code.
* Docker Compose brings up the long‑running services (sentinel/agents). Clients usually run from your host with `make run`.
* Env vars like `FAME_DIRECT_ADMISSION_URL` and provider keys (`OPENAI_API_KEY`, etc.) are used where relevant.

---

## Recommended learning path

1. **Start tiny — `examples/simple/`**
   Learn the core Agent APIs without networking or a sentinel:

   * wrap a function as an agent (`function_as_agent.py`)
   * one‑shot `run_task` vs background tasks (`agent_with_bg_task.py`)
   * basic RPC patterns (`rpc_agent.py`)
   * echo / ping‑pong for round‑trip mental model

2. **Single‑process with models — `examples/llm/`**
   Use the same Agent APIs to call external LLMs:

   * Q\&A function‑agent (`llm_agent.py`)
   * Chat agent with per‑session memory (`chat_agent.py`)
   * Image generation agent with a tiny viewer (`image_generation_agent.py`)
     *Goal:* see that “agent” is a programming model first; distribution is optional.

3. **Introduce the fabric — `distributed/hello/` → `hello-with-sentinel/`**
   Bring up a **sentinel** and a separate **agent** container; call the agent from a host client. Learn the admission URL and logical addresses (`echo@fame.fabric`).

4. **RPC on the fabric — `distributed/rpc/`**
   Expose operations with `@operation`, including **streaming** (e.g., Fibonacci stream). Call methods over the fabric like local methods.

5. **Long‑running work — `distributed/cancellable/` + `status-subscription/`**
   Use **A2A task APIs**: start a background task, subscribe to **status/artifact** updates, cancel mid‑flight.

6. **Push vs stream — `distributed/push-notifications/`**
   Contrast streaming with **callback‑style** notifications via an **on‑message** handler.

7. **Decoupling addresses — `distributed/capability-routing/`**
   Resolve providers by **capability** instead of hard‑coded logical addresses.

8. **Multi‑agent orchestration — `distributed/multi-agent/`**
   Launch multiple agents and orchestrate them with **scatter–gather** (`Agent.broadcast`). Example: summarizer + sentiment + aggregator.

9. **Topologies — `distributed/biomes/` and `distributed/peers/`**
   *Biomes:* hierarchical parent/child sentinels (deep‑to‑deep delegation across child biomes).
   *Peers:* two sentinels connected via a peer link; route calls across the peer.

9. **Monitoring — `monitoring/open-telemetry/`
   See how message envelopes flow across the fabric using OpenTelemetry and Jaeger for distributed tracing. This example shows how to:

   - Instrument agents and sentinels with OpenTelemetry.
   - Visualize RPC request and response traces in Jaeger.
   - Track the lifecycle of an envelope as it moves between nodes.
   - Diagnose bottlenecks and latency in multi-agent workflows.

   > Tip: After running `make start`, open the Jaeger UI (usually at [http://localhost:16686](http://localhost:16686)) to explore traces in real time.

11. **Security tiers — `security/`**
    Progressively add real‑world security:

    * **gated/**: OAuth2/JWT‑gated admission to the sentinel
    * **overlay/**: signed envelopes (provenance, tamper‑evidence)
    * **advanced/**: strict overlay + admission + SPIFFE/X.509 (SVID) identities and sealed channels (BSL add‑on)
    * **http‑connector/**: HTTP connector example for bridging agents/services
    * **stickiness/**: session‑affinity (sticky routing) across replicas

> Tip: Stop at any stage that fits your needs. If you just need distributed RPC today, you can live in `distributed/rpc` and return for security/topologies later.

---

## Quick prerequisites

* **Python 3.12+** if you run scripts locally
* **Docker + Docker Compose** for anything in `distributed/` or `security/`
* **OpenAI API key** for LLM‑backed examples: `export OPENAI_API_KEY=…`

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
* **agent\_ping\_pong.py**, **a2a\_agent.py** — tiny messaging exercises

### `llm/`

* **llm\_agent.py** — function‑agent does Q\&A with GPT
* **chat\_agent.py** — chat with per‑session memory (REPL)
* **image\_generation\_agent.py** — image generation; saves PNGs; optional local viewer

### `distributed/`

* **hello/** — echo across a real fabric (sentinel + agent)
* **hello-with-sentinel/** — same idea with explicit sentinel config
* **rpc/** — math agent with add/multiply + streaming Fibonacci
* **cancellable/** — background task with progress artifacts; client cancels at threshold
* **status-subscription/** — subscribe to status/artifact updates for long‑running tasks
* **push-notifications/** — register a callback endpoint and receive push messages
* **capability-routing/** — route requests by declared agent capabilities
* **multi-agent/** — summarizer + sentiment + aggregator; `Agent.broadcast` scatter–gather
* **biomes/** — hierarchical (parent/child) sentinels; deep‑to‑deep delegation across child biomes
* **peers/** — peer‑linked sentinels; calls hop across the peer link
* **stateful-conversation/** — conversation agent with persistent context/state

### `security/` (progressive)

* **gated/** — OAuth2 token‑gated admission; TLS via Caddy as reverse proxy
* **overlay/** — overlay signing (integrity, provenance) on messages
* **advanced/** — strict overlay + admission + CA‑issued SVIDs (SPIFFE/X.509); sealed channels
* **http-connector/** — bridge HTTP endpoints and agents via the connector example
* **stickiness/** — stickiness manager for session‑affinity routing across replicas

---

## What to learn in each stage

* **Agent model**: `BaseAgent`, `Agent.from_handler`, `run_task` vs `start_task`, artifacts and streams
* **Fabric mental model**: logical addresses, the sentinel as attach point, admission URL
* **RPC ergonomics**: `@operation` methods, request/response vs streaming
* **A2A tasks**: progress artifacts, status updates, cancellation & subscription
* **Push callbacks**: `on_message` handlers and `send_message` for notifications
* **Orchestration**: parallel fan‑out and result merging
* **Topologies**: hierarchical biomes vs peer links
* **Security**: OAuth2 (gated), overlay signing (integrity/provenance), sealed channels + SVIDs (advanced), HTTP connector, stickiness

---

## Troubleshooting quickies

* **Client can’t connect** → ensure `FAME_DIRECT_ADMISSION_URL` points to the sentinel (`ws://localhost:8000/...` from host; `ws://sentinel:8000/...` inside Compose).
* **No LLM output** → set `OPENAI_API_KEY`; verify model availability or override via `MODEL_NAME` when supported.
* **Agents don’t attach** → start the sentinel first; check env files in `security/*/config/`.
* **Peer/biome routes** → verify peer attach URL (`FAME_PEER_WS_URL`) or child upstream URL(s) for hierarchical setups.
* **Port 8000/443 in use** → change the Compose port mapping or free the port.

---

## Where to go next

* Extend the math RPC with your own operations (including streaming)
* Add micro‑agents (keyword extractor, NER, RAG) to the multi‑agent pipeline
* Turn on overlay signing in non‑security examples to compare envelope metadata
* Swap the OAuth dev server with your IdP; integrate your own CA for SVID issuance
* Experiment with **stickiness** to keep a conversation pinned to a replica
* Try the **HTTP connector** to bridge existing HTTP services into the fabric

---

Happy hacking! If you spot a rough edge, file an issue with the example name and any logs/commands you ran.
