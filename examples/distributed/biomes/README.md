# Hierarchical Fabric (Biome) Example — Parent/Child Sentinels + Deep‑to‑Deep Delegation

This example demonstrates a **hierarchical fabric** where a **main (parent) sentinel** fronts multiple **child sentinels**, each hosting its own agents. In Naylence, everything “behind” a sentinel is a **biome**. Here, two child biomes hang off a single main sentinel. It also showcases **deep‑to‑deep routing** by delegating a method call from one child biome to another through the main sentinel.

```
client  →  main sentinel  →  child sentinel 1  →  agent 1
                       └→  child sentinel 2  →  agent 2
```

The client attaches **only** to the main sentinel. Address resolution and routing traverse the sentinel tree to reach agents located in child biomes.

---

## What this shows

* **Biomes (hierarchical sentinels):** model separate domains behind each sentinel and stitch them into a single fabric.
* **Cross‑biome routing:** call agents in child biomes using **logical addresses**; the main sentinel forwards requests to the right child.
* **Deep‑to‑deep routing (delegation):** `math‑agent2` implements **`multiply`** by **delegating** the work to `math‑agent1`, demonstrating routing from one child biome to another **through the main sentinel**.
* **Mixed capabilities:** one agent serves arithmetic RPC (add/multiply), the other serves a **streaming** Fibonacci endpoint (and delegated multiply).
* **Simple admission (dev):** children and agents use **direct (open)** admission for clarity; production can switch to **gated/overlay/strict‑overlay** with the same topology.

---

## Files

* **`docker-compose.yml`** — brings up the main sentinel, two child sentinels, and two agents.

  * Child sentinels attach upstream via:

    * `FAME_ADMISSION_PROFILE=open`
    * `FAME_DIRECT_ADMISSION_URL=ws://main-sentinel:8000/fame/v1/attach/ws/downstream`
  * Agents attach to their **respective child** sentinel with the same `open` profile.
* **`sentinel.py`** — entrypoint for both main and child sentinels (using `configs.SENTINEL_CONFIG`).
* **`math_agent1.py`** — arithmetic RPC (`add`, `multiply`) at address **`math1@fame.fabric`**.
* **`math_agent2.py`** — **streaming** Fibonacci operation (`fib_stream`) **and a delegated** `multiply` (forwards to **`math1@fame.fabric`**) at **`math2@@fame.fabric`**.
* **`client.py`** — attaches to the **main** sentinel and calls both agents by address.
* **`common.py`** — shared addresses.
* **`Makefile`** — `start`, `run`, `run-verbose`, `stop` targets.

---

## Address propagation & binding

The **main sentinel** can resolve and route to agent addresses that are “hiding” in downstream child biomes. The client only needs the **logical agent address**—for example, `math1@fame.fabric` and `math2@@fame.fabric`—and the fabric handles discovery and routing across the hierarchy. There is **no centralized dedicated address registry**: child sentinels propagate address announcements **upstream** to the parent, and the parent binds calls dynamically to the correct child biome.

---

## How it works (flow)

1. **Main sentinel** starts and exposes `ws://localhost:8000` to the host.

2. **Child sentinel 1** and **child sentinel 2** start and **attach upstream** to the main sentinel using **direct (open)** admission and a WebSocket attach URL.

3. **Agents** start and attach to their **local child sentinel**.

4. **Client** attaches to the **main sentinel** and resolves logical addresses:

   * `math1@fame.fabric` → routed to **child sentinel 1 → agent 1**
   * `math2@@fame.fabric` → routed to **child sentinel 2 → agent 2**

5. **Deep‑to‑deep delegated multiply:** the client calls `multiply` on **`math2@@fame.fabric`**; `math‑agent2` delegates the call to **`math1@fame.fabric`**.

   Call path for `multiply`:

   ```
   client (multiply on math2@@fame.fabric)
      → main sentinel → child sentinel 2 → math‑agent 2
      → child sentinel 2 → main sentinel → child sentinel 1 → math‑agent 1
      → (result returns along the reverse path)
   ```

6. Requests/replies (and streams) traverse the sentinel tree transparently.

---

## Run it

```bash
make start       # start main sentinel, child sentinels, and agents
make run         # run client (calls math1.add/multiply, math2@.multiply (delegated), then math2@.fib_stream)
make run-verbose # same as run, but prints envelope metadata
make stop        # tear down
```

> The client uses `FAME_DIRECT_ADMISSION_URL=ws://localhost:8000/fame/v1/attach/ws/downstream` to attach to the main sentinel.

---

## Observing the hierarchy

* **Envelope logs:** use `make run-verbose` to watch routing metadata as calls traverse **main → child → agent** and back.
* **Delegation in action:** run `make run` and observe that a `multiply` requested on `math2@` ultimately executes on `math1` in the other biome.
* **Service isolation:** stop one child sentinel and note that only the agent in that biome becomes unreachable; the other biome continues to serve.
* **Streaming across biomes:** `fib_stream` demonstrates a streaming response flowing **up** from a child biome to the client with no code changes.

---

## When to use hierarchical fabrics

* **Network or organizational boundaries** where each biome (child sentinel) represents an environment, team, or region.
* **Blast‑radius control**: faults or restarts in one biome don’t take down others.
* **Policy and security segmentation**: each biome can run its own admission/security profile while still joining a larger fabric through the main sentinel.

---

## Security notes

This demo uses **`open`** admission for simplicity. In real deployments:

* Prefer **`gated`** (OAuth2/JWT) or **`overlay`** (signed envelopes) for OSS stacks.
* Use **`strict‑overlay`** (with the Advanced Security add‑on) for SPIFFE/X.509 identities and sealed overlay encryption; the hierarchical topology is unchanged.

---

## Troubleshooting

* **Client can’t connect** → confirm the main sentinel is healthy on port **8000** and the client’s `FAME_DIRECT_ADMISSION_URL` points to it.
* **Agent 1 not reachable** → check that **child‑sentinel1** attached to the main sentinel (healthcheck) and that **math‑agent1** attached to **child‑sentinel1**.
* **Agent 2 not reachable** → same as above, but for **child‑sentinel2/math‑agent2**.
* **Delegated multiply fails** → confirm `math‑agent1` is healthy and reachable; check that `math‑agent2` delegates to the correct logical (`math1@fame.fabric`).
* **Streams don’t print** → run with `make run-verbose` to confirm messages; ensure `fib_stream` is called with `_stream=True` in the client code.

---

## What to tweak next

* Add a **third child biome** and another agent to see fan‑out.
* Switch the child biomes to **`gated`** or **`overlay`** profiles.
* Introduce **wildcard logicals** and the **stickiness** manager (advanced security) to load‑balance replicas in a child biome.
* Place agents on separate hosts; set `FAME_PUBLIC_URL` on sentinels if your ingress sits behind TLS/hostnames.
