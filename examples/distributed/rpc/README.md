# Distributed RPC Example — Client ▸ Sentinel ▸ Agent

This example demonstrates **arbitrary RPC operations** in a **distributed topology**:

```
request: client ──▶ sentinel ──▶ math-agent
reply:   client ◀─ sentinel ◀─ math-agent
```

The goal is to show that methods exposed with the **`@operation`** decorator behave the **same** in distributed mode as they do locally — including **renaming** RPC endpoints and **streaming** results.

> ⚠️ **Security note:** This demo is intentionally **insecure** for clarity (no auth, TLS, or overlay security). Later examples add secure admission, identities, envelope signing, and sealed channels.

---

## What’s inside

* **Sentinel** — coordination node listening on `:8000`.
* **MathAgent** — exposes three RPC ops via `@operation`:

  * `add(x, y)` — simple sum.
  * `multiply(x, y)` — method is `multi(...)` but published as **`multiply`** via `@operation(name="multiply")`.
  * `fib_stream(n)` — **streaming** Fibonacci sequence using `@operation(streaming=True)`.
* **Client** — calls the operations and consumes the stream.

**Logical address:** `math@fame.fabric` (see `common.py`).

---

## Files

* `math_agent.py` — `BaseAgent` with `@operation` methods (rename + streaming examples).
* `client.py` — attaches to the fabric and invokes `add`, `multiply`, and `fib_stream` (async stream).
* `sentinel.py` — starts the sentinel in dev mode.
* `docker-compose.yml` — brings up **sentinel** and **math-agent** service.
* `common.py` — holds `AGENT_ADDR` (`math@fame.fabric`).

> Note: In Compose the agent service may be named `echo-agent` but it runs `math_agent.py`.

---

## Quick start (Docker Compose)

1. **Start services**

```bash
docker compose up -d
```

This starts:

* **sentinel** on `localhost:8000`
* **math-agent** connected downstream (uses `FAME_DIRECT_ADMISSION_URL` internally)

2. **Run the client (host)**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

**Expected output (example)**

```
7
42
0 1 1 2 3 5 8 13 21 34
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

## Standalone (no Compose)

Run each component in separate terminals using your local Python env:

**Terminal A — sentinel**

```bash
python sentinel.py
```

**Terminal B — agent**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python math_agent.py
```

**Terminal C — client**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

---

## The `@operation` decorator

```python
class MathAgent(BaseAgent):
    @operation                      # published as "add"
    async def add(self, x: int, y: int) -> int:
        return x + y

    @operation(name="multiply")     # rename RPC op
    async def multi(self, x: int, y: int) -> int:
        return x * y

    @operation(name="fib_stream", streaming=True)  # enable streaming
    async def fib(self, n: int):
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b
```

### Key points

* **Expose any method** as an RPC op with `@operation`.
* **Rename** the external RPC name via `@operation(name=...)` without changing your Python method name.
* **Streaming results** with `streaming=True`; yield inside the method and consume with `_stream=True` client-side:

```python
# client.py
async for v in await agent.fib_stream(_stream=True, n=10):
    print(v, end=" ")
```

The same code works **unchanged** in single-process and distributed setups.

---

## Troubleshooting

* **Client can’t connect** → ensure `FAME_DIRECT_ADMISSION_URL` points to the right sentinel (`localhost` on host; `sentinel` in Compose).
* **Agent fails to attach** → start **sentinel** first; check the env var in Compose.
* **Port already in use** → another process uses `8000`. Stop it or edit the Compose port mapping.

---

## Next steps

* Add auth & identities (SVID), envelope signing, and **overlay encryption**.
* Extend `MathAgent` with more RPCs (e.g., matrix ops), or add a second agent and compose calls.
* Demonstrate **backpressure** and cancellation on streaming RPCs.

---

This example proves that Naylence RPCs are **transport-agnostic**: define once with `@operation`, run anywhere — locally or across the fabric via a sentinel.
