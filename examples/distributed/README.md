# Distributed Examples with Naylence

This folder collects all **distributed setups** in Naylence.

**Distributed** means you don’t need to spin up your own HTTP servers or REST endpoints. Naylence provides its own **fabric layer** (sentinels, agents, and clients) that handle all transport, addressing, and routing out of the box.

Every example here runs entirely with **Docker Compose** — just `make start` and the stack comes alive. You can move the same setup into Kubernetes, Nomad, or any other containerized infrastructure with no code changes.

---

## What “Distributed” Means Here

- **Multiple processes/containers**: agents, clients, and sentinels are separate services.
- **Fabric-native networking**: no REST APIs, no gRPC servers — the fabric itself is the transport.
- **Logical addressing**: agents are invoked via names like `math@fame.fabric`, not by IP:port.
- **Routing out of the box**: sentinels propagate addresses, route requests, and relay streams — whether in parent/child (biomes) or peer-to-peer topologies.
- **Portable Compose setups**: each directory includes a `docker-compose.yml` and `Makefile` targets.  
  - `make start` → bring up the stack  
  - `make run` → run the sample client  
  - `make run-verbose` → show envelope routing  
  - `make stop` → tear it down

---

## Example Categories

- **hello/** — the simplest “echo” agent + client. Minimal, but already distributed (agent served separately, client attaches via sentinel).
- **hello-with-sentinel/** — adds a sentinel between client and agent (typical production topology).
- **rpc/** — shows distributed RPC calls (`@operation` endpoints, streaming, renaming).
- **cancellable/** — distributed background tasks with live updates + cancellation.
- **status-subscription/** — subscribe to task status/artifacts across the fabric.
- **push-notifications/** — callback-style cross-agent notifications.
- **multi-agent/** — orchestrator pattern with multiple collaborating agents (requires OpenAI key).
- **capability-routing/** — discover agents by capability instead of fixed address.
- **peers/** — two sentinels in peer topology (no parent/child).
- **biomes/** — hierarchical sentinel setup (main + children).

---

## Moving Beyond Compose

- All examples are **container-first**: you can move the same Compose services into Kubernetes or other schedulers.
- Swap `open` admission (default) with **gated, overlay, or strict-overlay** for real security.
- Scale out: add more agents or sentinels, or replicate agents and load-balance with wildcard logicals.

---

> **Tip:** If you’re coming from a REST-first background — you don’t need Flask/FastAPI here. Naylence already provides the transport, routing, and addressing out of the box. REST is optional, not required.