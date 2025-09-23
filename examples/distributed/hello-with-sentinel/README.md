# Hello: Sentinel + Agent + Client

A slightly more complete **distributed example** for Naylence that runs a **sentinel**, an **echo agent**, and a **client**. It shows a typical topology where an agent registers through a sentinel and a client attaches to the fabric to invoke the agent by **logical address**.

> ⚠️ **Security note:** This demo is intentionally insecure for clarity. There is **no auth, TLS, or overlay security** enabled here. Later examples will layer in secure admission, identities, and sealed channels.

---
> **For curious souls:** Naylence ships with FastAPI/Uvicorn under the hood but you’ll never need to see or configure it. All transport, routing, and addressing are handled by the fabric itself. No boilerplate servers, no route wiring, just `make start` and go.
---

## What’s inside

* **Sentinel** — coordination node that accepts downstream connections on `:8000`.
* **EchoAgent** — trivial agent that echoes whatever payload it receives.
* **Client** — short‑lived process that sends a message and prints the response.

```
request: client ──▶ sentinel ──▶ echo-agent
reply:   client ◀─ sentinel ◀─ echo-agent
```

**Logical address:** `echo@fame.fabric` (defined in `common.py`).

*All client requests and agent replies are routed through the sentinel — there is no direct client↔agent channel in this topology.*

---

## Files

* `sentinel.py` — starts a sentinel (dev config).
* `echo_agent.py` — `BaseAgent` with async `run_task` that returns the payload.
* `client.py` — attaches to the fabric and calls `run_task("Hello, World!")`.
* `docker-compose.yml` — services for sentinel and agent, plus healthcheck.

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

## Alternative: Quick start (Docker Compose)

1. **Start services**

```bash
docker compose up -d
```

This brings up:

* **sentinel** on `localhost:8000` (with a lightweight healthcheck)
* **echo-agent** connected to the sentinel (uses `FAME_DIRECT_ADMISSION_URL`)

2. **Run the client (host)**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

**Expected output**

```
Hello, World!
```

3. **Stop**

```bash
docker compose down --remove-orphans
```

---

## Alternative: run the client in Docker

```bash
docker run --rm \
  -v "$PWD:/work:ro" -w /work \
  --network "$(basename "$PWD")_naylence-net" \
  -e FAME_DIRECT_ADMISSION_URL="ws://sentinel:8000/fame/v1/attach/ws/downstream" \
  naylence/agent-sdk-python \
  python client.py
```

---

## Standalone Python (no Compose)

If you prefer to run both processes locally with your own Python env (the repo provides `pyproject.toml`):

1. **Start sentinel**

```bash
python sentinel.py
```

2. **Start the agent** (new terminal)

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python echo_agent.py
```

3. **Run the client** (another terminal)

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

---

## How it works

* **Agent:** Implements `BaseAgent.run_task(payload, id)` as an async coroutine; returning the payload makes it an echo.
* **Registration:** The agent connects **downstream** to the sentinel via `FAME_DIRECT_ADMISSION_URL`.
* **Client:** Creates a remote handle with `Agent.remote(address=AGENT_ADDR)` and awaits `run_task(...)`.
* **Addressing:** Components refer to the agent via its **logical address** `echo@fame.fabric`.

---

## Troubleshooting

* **Client hangs / fails to connect** → ensure `FAME_DIRECT_ADMISSION_URL` points to the sentinel you’re using (`localhost` from host, `sentinel` inside Compose network).
* **Agent fails to start** → start the sentinel first; the agent depends on it.
* **Port in use** → something is already bound to `8000`. Stop it or change the mapping in `docker-compose.yml`.

---

## Next steps

* Swap the echo behavior with custom logic in `run_task` (long‑running tasks are fine — it’s fully async).
* Introduce **security**: SVID‑backed identities, envelope signing, overlay encryption, and policy‑based admission.
* Add more agents and route by capability or by logical addresses.

---

This example is a bridge between the minimal echo demo and the security‑enabled scenarios that follow. It’s designed for easy iteration: long‑running **sentinel/agent** in Compose, short‑lived **client** on demand.
