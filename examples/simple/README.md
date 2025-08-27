# Naylence Agent SDK Basics — Single‑Process Examples

These examples run **agent and client in the same process**. They’re meant to teach the **core Agent SDK** concepts without any distributed wiring (no sentinel, no fabric admission URLs, no Docker networking). Each script starts a local fabric, serves an agent, obtains a typed proxy, makes a call, and prints results.

> ⚠️ **Security note:** For clarity, these examples use **no authentication or encryption**. Later examples introduce secure identities, admission, and overlay encryption.

---

## What you’ll learn

* Spinning up a local `FameFabric` context
* Serving a `BaseAgent` (or turning a function into an agent)
* Calling methods via a typed client proxy (`Agent.remote_by_address(...)`)
* Defining RPC operations (including **streaming**)
* Using the **A2A task model** (`start_task`, `get_task_status`)
* Simulating **background / long‑running** work

---

## Example catalog

| File                    | Concept                        | What it does                                                                         |
| ----------------------- | ------------------------------ | ------------------------------------------------------------------------------------ |
| `echo_agent.py`         | **Minimal agent**              | Implements `BaseAgent.run_task` and echoes the payload back.                         |
| `function_as_agent.py`  | **Function → Agent**           | Wraps a plain async function with `Agent.from_handler` and returns the current time. |
| `rpc_agent.py`          | **RPC operations & streaming** | Uses `@operation` to expose `add(x, y)` and a streaming Fibonacci generator.         |
| `agent_with_bg_task.py` | **Background tasks**           | Returns `WORKING` immediately; status transitions to `COMPLETED` after async work.   |
| `a2a_agent.py`          | **A2A minimal flow**           | Implements `start_task` to instantly return a `COMPLETED` task with a payload.       |
| `agent_ping_pong.py`    | **Agent‑to‑Agent calls**       | `PingAgent` forwards a task to `PongAgent` and returns the result.                   |

---

## Prerequisites

* **Python 3.12+** (recommended)
* Project dependencies installed (e.g., `pip install -e .` from repo root, or `poetry install`) so that `naylence.agent` and `naylence.fame` are importable.

> Optional: You can also run any script inside a ready‑made container image (see **Run in Docker** below).

---

## Quick start (local Python)

Run any script directly:

```bash
python echo_agent.py
python function_as_agent.py
python rpc_agent.py
python agent_with_bg_task.py
python a2a_agent.py
python agent_ping_pong.py
```

Expected behaviors:

* **echo\_agent.py** → prints `Hello, World!`
* **function\_as\_agent.py** → prints an ISO timestamp (UTC)
* **rpc\_agent.py** → prints `7`, then a stream of Fibonacci numbers
* **agent\_with\_bg\_task.py** → prints WORKING → (after delay) COMPLETED
* **a2a\_agent.py** → prints `Agent address: ...` then `Result: ...` with COMPLETED
* **agent\_ping\_pong.py** → prints Pong reply for the forwarded message

---

## Run in Docker (optional)

A convenience `docker-compose.yml` is provided to run each script in an isolated container.

Start one of the services, for example the RPC agent:

```bash
docker compose up rpc-agent
```

Or run a one‑off container for a given script:

```bash
docker run --rm \
  -v "$PWD:/work:ro" -w /work \
  ghcr.io/naylence/agent-sdk-base:0.1.8 \
  python rpc_agent.py
```

---

## How it works (all scripts)

1. **Create a fabric:** `async with FameFabric.create() as fabric:`
2. **Serve an agent:** `agent_address = await fabric.serve(MyAgent(...))`
3. **Get a client proxy:** `remote = Agent.remote_by_address(agent_address)`
4. **Call the agent:**

   * `await remote.run_task(payload=...)` **or**
   * `await remote.some_rpc_method(args...)` **or**
   * `await remote.start_task(...)` / `await remote.get_task_status(...)`

Because everything runs in one process, the fabric routes calls in‑memory with minimal ceremony.

---

## Troubleshooting

* **Import errors** → ensure the Naylence packages are installed in your env.
* **Event loop errors** → make sure you run scripts directly (`python script.py`) and not from inside another running loop.
* **Nothing prints** → some examples rely on async delays (e.g., background tasks). Give them a moment, or increase the sleep.

---

## Next steps

* Move to the **distributed echo** example (sentinel + agent + client) to see remote attachment via admission URLs.
* Explore **security‑enabled** examples for identities, envelope signing, and overlay encryption.
* Try adding your own RPC methods with `@operation` or swap `run_task` logic for real work.

---

These single‑process scripts are the fastest way to learn the **shape** of a Naylence agent before deploying it in a distributed, secure topology.
