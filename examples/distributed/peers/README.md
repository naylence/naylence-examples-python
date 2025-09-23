# Peer‑to‑Peer Fabric Example — Two Sentinels, One Client

This example demonstrates a **peer topology** where **two sentinels are peers** (no parent/child). Each sentinel hosts its own agent, and a **single client attached to one sentinel** can call **both agents**. Routing crosses the peer link transparently.

---
Flow:
```
client  →  peer‑sentinel1  ↔  (peer link)  ↔  peer‑sentinel2
             │                                   │
             └── math1@fame.fabric               └── math2@fame.fabric
```

Unlike hierarchical biomes, there is **no upstream/downstream** relationship here. Address propagation happens **between peers**, and the fabric routes accordingly **without a centralized registry**.

---

## What this shows

* **Peer sentinels (no parent/child):** sentinels connect via a dedicated **peer attach** route.
* **Cross‑peer routing:** the client attaches to **peer‑sentinel1** and calls `math2@fame.fabric` hosted behind **peer‑sentinel2**.
* **Address propagation w/out registry:** peers exchange address announcements across the link; the client still uses plain logical addresses.
* **Mixed operations:** `math1` exposes `add`/`multiply` (RPC); `math2` exposes a **streaming** `fib_stream`.
* **Dev‑friendly admission:** everything runs in **`open`** profile for clarity; production can switch to **gated/overlay/strict‑overlay**.


---
> ⚠️ **Security note:** This demo is intentionally insecure for clarity. There is **no auth, TLS, or overlay security** enabled here. Later examples will layer in secure admission, identities, and sealed channels.

---
> **For curious souls:** Naylence ships with FastAPI/Uvicorn under the hood but you’ll never need to see or configure it. All transport, routing, and addressing are handled by the fabric itself. No boilerplate servers, no route wiring, just `make start` and go.
---

## Files

* **`docker-compose.yml`** — starts **peer‑sentinel1**, **peer‑sentinel2**, and two agents.

  * `peer‑sentinel1` listens on **8000** (host port mapped).
  * `peer‑sentinel2` peers to sentinel1 via `FAME_PEER_WS_URL = ws://peer-sentinel1:8000/fame/v1/attach/ws/peer` and also uses direct open admission for container wiring.
  * `math-agent1` attaches to **peer‑sentinel1**; `math-agent2` attaches to **peer‑sentinel2**.
* **`peer_sentinel1.py`** — dev‑mode sentinel.
* **`peer_sentinel2.py`** — custom config with a **`peers: [{ direct_url: ${FAME_PEER_WS_URL} }]`** entry and WebSocket listener.
* **`math_agent1.py`** — RPC `add`/`multiply` at **`math1@fame.fabric`**.
* **`math_agent2.py`** — **streaming** `fib_stream` at **`math2@fame.fabric`**.
* **`client.py`** — attaches to **peer‑sentinel1** and calls `math1` + `math2` by **address**.
* **`common.py`** — shared addresses: `MATH_AGENT1_ADDR`, `MATH_AGENT2_ADDR`.
* **`Makefile`** — `start`, `run`, `run-verbose`, `stop`.

---

## Key environment variables

* **Client / host:** `FAME_DIRECT_ADMISSION_URL=ws://localhost:8000/fame/v1/attach/ws/downstream` (attach to **peer‑sentinel1**).
* **peer‑sentinel2:**

  * `FAME_PEER_WS_URL=ws://peer-sentinel1:8000/fame/v1/attach/ws/peer` (peer link target)
  * `FAME_ADMISSION_PROFILE=open`
  * `FAME_DIRECT_ADMISSION_URL=ws://peer-sentinel1:8000/fame/v1/attach/ws/downstream` (container wiring for open admission)
* **Agents:** `FAME_ADMISSION_PROFILE=open` + appropriate `FAME_DIRECT_ADMISSION_URL` to their local sentinel.

---

## How it works (flow)

1. **peer‑sentinel1** starts and exposes **ws\://localhost:8000** to the host.
2. **peer‑sentinel2** starts, **dials the peer link** to sentinel1 using the **peer attach** route (`/fame/v1/attach/ws/peer`).
3. **math‑agent1** attaches to peer‑sentinel1; **math‑agent2** attaches to peer‑sentinel2.
4. **Client** attaches to peer‑sentinel1 and calls by address:

   * `math1@fame.fabric` → stays on **peer‑sentinel1** → **math‑agent1**.
   * `math2@fame.fabric` → crosses the **peer link** to **peer‑sentinel2** → **math‑agent2** (streams flow back over the same link).

No centralized registry is needed: **address announcements** are exchanged across the peer link, and routing is computed on demand.

---

## Run it

```bash
make start       # start both sentinels and agents
make run         # run client (RPC on math1 + streaming fib on math2 via peer link)
make run-verbose # same as run, but prints envelope metadata, including peer routing
make stop        # tear down
```

> Tip: watch `docker compose logs -f peer-sentinel2` while running the client to see the peer link in action.

---

## Troubleshooting

* **Client can’t reach math2**

  * Ensure **peer‑sentinel2** is healthy and `FAME_PEER_WS_URL` points to **peer‑sentinel1**’s **/fame/v1/attach/ws/peer** endpoint.
  * Check that `math-agent2` attached to **peer‑sentinel2** (container health and logs).
* **Client can’t connect at all**

  * Verify `peer‑sentinel1` is healthy on **8000**; confirm your client’s `FAME_DIRECT_ADMISSION_URL`.
* **No stream output**

  * Call `fib_stream` with `_stream=true` and try `make run-verbose` to observe envelopes and the peer hop.

---

## Variations to try

* **Bi‑directional peers:** add a peer entry on sentinel1 back to sentinel2 and observe symmetric peering.
* **Multiple peers / mesh:** add a third sentinel and route across two hops.
* **Security profiles:** switch to **overlay** (signed envelopes) or **strict‑overlay** (Advanced Security) to see integrity/identity propagate across peers.
* **Capability routing across peers:** advertise a capability on both sides and resolve providers dynamically.
