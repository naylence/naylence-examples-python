# Hello Example

This example demonstrates the **simplest distributed setup** using the Naylence Agent SDK. It consists of two components:

* **EchoAgent** — a minimal agent that simply echoes back any payload it receives.
* **Client** — a short‑lived program that sends a message to the agent and prints the response.

In this demo, the agent is hosted directly on a **sentinel node**, and the client connects directly to it. In real production setups, agents usually run behind sentinels, and clients don’t talk to agents directly — but for simplicity, we bend the rules here.

> ⚠️ **Security note:** This example does **not** feature any security mechanisms. It is kept intentionally minimal for learning purposes. Later examples in this repository will introduce secure configurations.

---
> **For curious souls:** Naylence ships with FastAPI/Uvicorn under the hood but you’ll never need to see or configure it. All transport, routing, and addressing are handled by the fabric itself. No boilerplate servers, no route wiring, just `make start` and go.
---

## Components

### EchoAgent

* Implemented in [`echo_agent.py`](echo_agent.py).
* Extends `BaseAgent` from the Naylence Agent SDK — the simplest way to build a new agent.
* Overrides `run_task` (fully async), which can support long‑running tasks.
* Assigned a **logical address** (`echo@fame.fabric`) defined in [`common.py`](common.py), so other components can reference it.

### Client

* Implemented in [`client.py`](client.py).
* Creates a remote handle to the agent by its logical address.
* Sends the string `"Hello, World!"` as a task.
* Prints the agent’s echoed response.

Expected output:

```
Hello, World!
```

---

## Quick start

> Requirements: Docker + Docker Compose installed.

From this example folder:

```bash
make start       # 🚀 brings up the stack (sentinel + echo-agent)
```

Run the sample client against the echo agent:

```bash
make run         # ▶️ executes client.py
```

Shut down when done:

```bash
make stop        # ⏹ stop containers
```

### See envelope traffic

Use the verbose target to print every **envelope** as it travels through the fabric:

```bash
make run-verbose
```

---

## Alternative: Running the Example

There are two other ways to run the components:

### 1. Standalone Python

Make sure your Python environment is set up (the project includes a `pyproject.toml`).

Start the agent (long‑running service):

```bash
python echo_agent.py
```

In another terminal, run the client:

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

---

### 2. Docker Compose (manual)

Start the echo agent via Compose:

```bash
docker compose up -d
```

This starts:

* A sentinel on `localhost:8000`
* The `echo-agent` connected to that sentinel

Run the client locally:

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

Stop services when done:

```bash
docker compose down --remove-orphans
```

Optionally, run the client inside Docker:

```bash
docker run --rm \
  -v "$PWD:/work:ro" -w /work \
  --network "$(basename "$PWD")_naylence-net" \
  -e FAME_DIRECT_ADMISSION_URL="ws://echo-agent:8000/fame/v1/attach/ws/downstream" \
  naylence/agent-sdk-python \
  python client.py
```

---

## Notes

* Agents are typically **long‑running services** (run via Compose).
* Clients are typically **short‑lived** and run on demand (for faster iteration).
* In Compose networking, use `echo-agent:8000`; from your host, use `localhost:8000`.

---

This example is intentionally minimal — a first step toward building more complex and **secure** multi‑agent distributed systems with Naylence.
