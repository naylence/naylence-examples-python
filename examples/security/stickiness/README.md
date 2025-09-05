# Advanced Secure Stickiness — Load‑Balanced Replicas with Strict Overlay (BSL)

This example demonstrates **secure load balancing with stickiness** using the **Naylence Advanced Security** package (BSL‑licensed). It launches **two math‑agent replicas**, enables **channel‑level overlay encryption**, and configures the **sentinel** to keep a client’s encrypted flow pinned to **one specific replica**. The same replica handles the **channel setup** request and all **subsequent data** requests.

> Requires the advanced image/add‑on (e.g., `naylence/agent-sdk-adv-python`) and `FAME_SECURITY_PROFILE=strict-overlay`.

---

## What this shows

* **Replica fan‑out via logical wildcards** (agents): a single logical (e.g., `math@fame.fabric`) can be backed by multiple replicas when agents request a wildcard namespace.
* **Secure stickiness** (sentinel): the sentinel’s stickiness manager pins a caller’s traffic to a single replica once an **encrypted channel** is established.
* **Channel encryption**: `FAME_DEFAULT_ENCRYPTION_LEVEL=channel` ensures payload confidentiality in addition to envelope signing.
* **Advanced admission & identity**: strict‑overlay requires **SPIFFE/X.509** identities and the **welcome + CA** flow (provided here for dev by containers).

## Why channel encryption in this demo

We intentionally use **channel encryption** here because it **only works with stickiness enabled**. Establishing a secure channel is a **multi-message interaction**—key requests/responses → opening the secure channel → sending data over that channel. For cryptographic continuity, **every message in that sequence must reach the same agent replica**. If requests were to bounce between replicas, the channel context (keys/state) would be missing and the flow would fail. The sentinel’s **AFTLoadBalancerStickinessManager** enforces this by routing the channel setup and all subsequent data frames to the **same replica**.

---

## Key configs

### 1) Agent — enable replicas with a wildcard logical

> This requires a **custom node config** (not the `dev_mode` presets). Mount as `/etc/fame/fame-config.yml`.

```yaml
node:
  type: Node
  requested_logicals:
    - "*.fame.fabric"  # Important! Use a wildcard to enable load balancing!
  security:
    type: SecurityProfile
    profile: ${env:FAME_SECURITY_PROFILE}
  admission:
    type: AdmissionProfile
    profile: ${env:FAME_ADMISSION_PROFILE}
```

* Each replica process serves the **same agent address** (e.g., `math@fame.fabric`).
* The **wildcard** tells the fabric that multiple nodes may advertise services under this logical domain, allowing the sentinel to distribute traffic.

### 2) Sentinel — turn on advanced stickiness

> Mount as `/etc/fame/fame-config.yml` for the sentinel container.

```yaml
node:
  type: Sentinel
  id: "${env:FAME_NODE_ID:}"
  public_url: "${env:FAME_PUBLIC_URL:}"
  listeners:
    - type: WebSocketListener
      port: "${env:FAME_SENTINEL_PORT:8000}"
  requested_logicals:
    - fame.fabric
  security:
    type: SecurityProfile
    profile: "${env:FAME_SECURITY_PROFILE:open}"
  admission:
    type: AdmissionProfile
    profile: "${env:FAME_ADMISSION_PROFILE:none}"
  storage:
    type: StorageProfile
    profile: "${env:STORAGE_PROFILE:memory}"

  # Important: enable advanced stickiness
  stickiness:
    type: AFTLoadBalancerStickinessManager
    security_level: strict
```

* `security_level: strict` enforces **secure, identity‑aware stickiness**: the same cryptographic context (client identity + channel setup) routes to the same replica.
* With **channel encryption** enabled, the **initial channel request** and all **subsequent frames** go to the same replica.

---

## Environment highlights

Set in the provided `.env` examples (agent/client/sentinel):

* `FAME_SECURITY_PROFILE=strict-overlay` — turns on strict overlay (advanced security; BSL add‑on).
* `FAME_DEFAULT_ENCRYPTION_LEVEL=channel` — opts into channel‑level encryption of payloads.
* `FAME_ADMISSION_PROFILE=welcome` — uses the **Welcome** service for placement and attach tickets.
* `FAME_CA_SERVICE_URL=…` and `FAME_CA_CERTS=…` — obtain and trust **SPIFFE/X.509** workload certs.

> The example ships a dev **OAuth2**, **Welcome**, and **CA**; these are for learning only. Replace with your IdP and CA in real deployments.

---

## How the flow works

1. **Admission** — The client/agents obtain an OAuth2 token; **Welcome** validates it and issues **placement** + **attach tickets**.
2. **Identity** — Each agent replica requests a **SPIFFE/X.509** cert from **CA** and joins the fabric.
3. **Wildcard backing** — Because replicas requested `*.fame.fabric`, the sentinel recognizes multiple providers for `math@fame.fabric`.
4. **First request** — Client calls `math@fame.fabric`. With `strict-overlay` and **channel** encryption, the sentinel picks a replica and **establishes the encrypted channel**.
5. **Stickiness** — The sentinel’s **AFTLoadBalancerStickinessManager** pins subsequent requests in that channel/context to the **same replica**.
6. **Failover** — If the chosen replica goes away, the sentinel selects another replica; the channel will be re‑established (and the stickiness updated accordingly).

---

## Running the example

```bash
make start       # brings up Caddy (TLS), OAuth2, Welcome, CA, Sentinel, and two math‑agent replicas
make run         # runs the client (add/multiply/fib_stream) against the sticky, encrypted path
make stop        # tears down containers
make clean       # removes generated certs, dev secrets, etc.
```

> Images referenced are the advanced (BSL) builds, e.g. `naylence/agent-sdk-adv-python`.

---

## How to verify stickiness

* **Watch agent logs:**

  * In one terminal: `docker compose logs -f math-agent-replica1`
  * In another: `docker compose logs -f math-agent-replica2`
  * Run `make run` a few times: you should see **only one** replica serving the client’s requests until you restart the client (or the replica).
* **Kill one replica:** `docker compose stop math-agent-replica1` → subsequent calls will **fail over** to replica2; re‑enable replica1 and observe stickiness on new channel setup.
* **Verbose envelopes:** `make run-verbose` to confirm **encryption metadata** on frames.

---

## Troubleshooting

* **Requests bounce between replicas**

  * Ensure the agent config includes `requested_logicals: ["*.fame.fabric"]` and the **custom YAML** is mounted.
  * Confirm sentinel config has the **`stickiness`** block with `AFTLoadBalancerStickinessManager`.
  * Verify both replicas serve the **same address** (e.g., `math@fame.fabric`).
* **No encryption visible**

  * Make sure `FAME_DEFAULT_ENCRYPTION_LEVEL=channel` is set and you’re using the advanced image.
* **Agents fail to attach**

  * Start order: sentinel healthy before agents; check Welcome/CA endpoints and `SSL_CERT_FILE` trust chain.
* **TLS / JWKS issues**

  * Use the Caddy‑generated CA in all containers; verify issuer/audience in JWT settings.

---

## Learn more

* **Advanced Security (BSL add‑on):** [https://github.com/naylence/naylence-advanced-security-python](https://github.com/naylence/naylence-advanced-security-python)
* **Runtime (fabric & profiles):** [https://github.com/naylence/naylence-runtime-python](https://github.com/naylence/naylence-runtime-python)
* **Agent SDK (build agents):** [https://github.com/naylence/naylence-agent-sdk-python](https://github.com/naylence/naylence-agent-sdk-python)
* **Examples (runnable demos):** [https://github.com/naylence/naylence-examples-python](https://github.com/naylence/naylence-examples-python)

---

> Production note: this demo is wired for learning. For real deployments, integrate your own IdP, CA, and policy engine, and pin exact image versions; don’t reuse dev secrets.
