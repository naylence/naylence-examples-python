# Capability Routing Example — Addressless Agent Discovery

This example shows how to call an agent **by capability** instead of by a fixed logical address. Rather than hard‑coding `math@fame.fabric`, the client asks the fabric for “any agent that provides the **math capability**,” and the fabric returns a remote proxy to the matching agent.

---

## Why route by capability?

* **Decoupling** — clients don’t need to know exact addresses, only the capability they need.
* **Replaceable implementations** — swap or upgrade agents without touching clients.
* **Scale‑out ready** — multiple agents can advertise the same capability; the fabric can choose a suitable provider.

---

## What this demonstrates

* Defining a **custom capability** tag (`fame.capability.math`).
* An agent that **advertises capabilities** (the built‑in `agent` plus `math`).
* A client that resolves a provider via `Agent.remote_by_capabilities([...])` and then calls `add`, `multiply`, and a **streaming** `fib_stream`.

---
> ⚠️ **Security note:** This demo is intentionally insecure for clarity. There is **no auth, TLS, or overlay security** enabled here. Later examples will layer in secure admission, identities, and sealed channels.

---
> **For curious souls:** Naylence ships with FastAPI/Uvicorn under the hood but you’ll never need to see or configure it. All transport, routing, and addressing are handled by the fabric itself. No boilerplate servers, no route wiring, just `make start` and go.
---

## Files

* **`docker-compose.yml`** — starts a sentinel and one math agent container.
* **`sentinel.py`** — minimal dev‑mode sentinel entrypoint.
* **`math_agent.py`** — a `BaseAgent` that exposes `add`, `multiply`, and streaming `fib_stream`, and advertises capabilities.
* **`client.py`** — attaches to the sentinel and **discovers the agent by capability**.
* **`common.py`** — defines the capability constant `MATH_CAPABILITY = "fame.capability.math"`.
* **`Makefile`** — `start`, `run`, `run-verbose`, `stop` targets.

---

## Key concepts

**1) Declare capabilities on the agent**

In `math_agent.py` the agent returns a list of capabilities:

```python
from common import MATH_CAPABILITY
from naylence.fame.core import AGENT_CAPABILITY

class MathAgent(BaseAgent):
    def __init__(self, name: str | None = None):
        super().__init__(name=name)
        self._capabilities = [AGENT_CAPABILITY, MATH_CAPABILITY]

    @property
    def capabilities(self):
        return self._capabilities
```

**2) Discover a provider by capability**

In `client.py` the client asks the fabric for any agent that satisfies the **required set** of capabilities:

```python
from naylence.agent import Agent
from naylence.fame.core import AGENT_CAPABILITY
from common import MATH_CAPABILITY

math_agent = Agent.remote_by_capabilities([AGENT_CAPABILITY, MATH_CAPABILITY])
```

Then it calls operations as usual (including streaming):

```python
print(await math_agent.add(x=3, y=4))
print(await math_agent.multiply(x=6, y=7))
async for v in await math_agent.fib_stream(n=10, _stream=True):
    print(v, end=" ")
```

---

## How it works (flow)

1. **Sentinel** starts and listens on port **8000**.
2. **Math agent** attaches to the sentinel and advertises its capability list.
3. **Client** attaches to the sentinel and requests a provider by capability.
4. The fabric resolves a matching agent, returns a proxy, and routes calls/streams normally.

---

## Run it

```bash
make start       # start sentinel and math agent
make run         # run client (capability discovery + add/multiply + fib_stream)
make run-verbose # same as run, with envelope metadata
make stop        # tear down
```

> The client uses `FAME_DIRECT_ADMISSION_URL=ws://localhost:8000/fame/v1/attach/ws/downstream` to attach to the sentinel; the agent uses the in‑compose URL `ws://sentinel:8000/...`.

---

## Troubleshooting

* **“No provider found”**

  * Ensure the agent is running and advertises the expected capability value: `fame.capability.math`.
  * Double‑check the client’s list: it should include both `AGENT_CAPABILITY` and `MATH_CAPABILITY`.
* **Client connects but calls fail**

  * Verify `FAME_DIRECT_ADMISSION_URL` is set appropriately for host vs. container contexts.
* **No stream output**

  * Make sure `fib_stream` is invoked with `_stream=True` and try `make run-verbose` to observe envelope flow.

---

## Variations to try

* **Multiple providers** — start two math agents advertising the same capability to see selection behavior.
* **Composite capabilities** — add another tag (e.g., `fame.capability.stats`) and require both in `remote_by_capabilities([...])`.
* **Address fallback** — keep a known address for emergencies, but use capability routing for the happy path.

---

*Back to the* **Examples Summary**.
