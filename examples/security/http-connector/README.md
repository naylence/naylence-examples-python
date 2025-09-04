# HTTP Connector Example — Direct HTTP Admission + Overlay Callback

This example shows how to run a Naylence agent over the **HTTP connector** instead of the default full‑duplex **WebSocket** connector. Because HTTP is not full‑duplex, the runtime combines **two half‑duplex links**:

1. **Downstream (agent ➜ sentinel)** — the agent initiates an **HTTP** connection to deliver its outbound traffic and attach request.
2. **Upstream (sentinel ➜ agent)** — the sentinel performs a **callback HTTP** connection back to the agent (using a JWT grant), completing a logical full‑duplex path.

The end result: clients can keep using WebSockets (or HTTP) to talk to the sentinel, while this agent speaks HTTP only.

---

## What’s different in this example

* **Connector:** uses **HTTP** for agent ↔ sentinel instead of WebSockets.
* **Two half‑duplex flows:** `downstream` and `upstream` HTTP routes together emulate full‑duplex.
* **Reverse authorization:** sentinel callback is authorized via a **JWT (HMAC)** that the agent grants.
* **Custom node config:** the agent runs from a **bespoke YAML config**, not `dev_mode` presets.
* **Public URL override:** sets **`FAME_PUBLIC_URL`** so the agent advertises a hostname reachable **from the sentinel** inside Docker.
* **Caddy mapping:** reverse proxy is configured for **both** WebSocket and HTTP ingress paths (for sentinel and agent).
* **Profiles in use:** `FAME_ADMISSION_PROFILE=direct-http` and `FAME_SECURITY_PROFILE=overlay-callback`.

---

## How it works (flow)

1. **Agent boots** with an **HTTP listener** and prepares a **callback connection grant** for its parent sentinel.
2. The **grant** includes a **Bearer JWT** signed using **HMAC**; the secret comes from `FAME_HMAC_SECRET`.
3. The agent sends a **node attach** request **(downstream)** to the sentinel’s HTTP ingress.
4. The sentinel validates the request and then establishes a **callback HTTP connection (upstream)** to the agent’s advertised URL.
5. The callback uses the grant’s **JWT** (audience validated via `FAME_JWT_REVERSE_AUTH_AUDIENCE`).
6. With both links up, messages flow in both directions over HTTP (half‑duplex each way). Clients may still talk to the sentinel over **WebSockets**.

---

## Key files (this example)

* **`config/math-agent-config.yml`** — custom node config:

  * `listeners: [ { type: HttpListener, port: ${FAME_AGENT_PORT} } ]`
  * `admission: DirectAdmissionClient` with an **`HttpConnectionGrant`**
  * grant `auth: BearerTokenHeaderAuth` using OAuth2 for the initial attach and HMAC‑JWT for the callback
* **`config/Caddyfile`** — reverse proxy for:

  * **Sentinel**:

    * WebSocket attach: `/fame/v1/attach/ws/*`
    * HTTP ingress (downstream): `/fame/v1/ingress/downstream/*`
  * **Agent**:

    * HTTP ingress (upstream callback): `/fame/v1/ingress/upstream`
* **`.env.*`** — per‑service environment:

  * `config/.env.agent` — agent variables (HTTP listener, reverse auth, HMAC secret)
  * `config/.env.sentinel` — sentinel security profile and trust
  * `config/.env.client` — client still connects via **WebSocket** for convenience

---

## Important environment variables

**Agent (****`config/.env.agent`****)**

```ini
FAME_PUBLIC_URL=https://math-agent          # hostname the agent advertises to the sentinel (Docker network alias)
FAME_AGENT_PORT=8001                        # agent HTTP listener port
FAME_SECURITY_PROFILE=overlay-callback      # enables reverse authorization & overlay signing
FAME_ADMISSION_PROFILE=direct-http          # direct admission over HTTP(S)
FAME_DIRECT_ADMISSION_URL=https://sentinel/fame/v1/ingress/downstream
FAME_ADMISSION_TOKEN_URL=https://oauth2-server/oauth/token
FAME_ADMISSION_CLIENT_ID=...
FAME_ADMISSION_CLIENT_SECRET=...
FAME_JWT_AUDIENCE=fame.fabric
FAME_JWT_TRUSTED_ISSUER=https://oauth2-server
FAME_JWT_REVERSE_AUTH_AUDIENCE=dev.naylence.ai
FAME_HMAC_SECRET=...                        # secret used to sign the callback JWT (HMAC)
SSL_CERT_FILE=/work/config/caddy/.../root.crt
```

**Sentinel (****`config/.env.sentinel`****)**

```ini
FAME_SECURITY_PROFILE=overlay               # sentinel runs with overlay signing
FAME_JWT_TRUSTED_ISSUER=https://oauth2-server
FAME_JWT_AUDIENCE=fame.fabric
SSL_CERT_FILE=/work/config/caddy/.../root.crt
```

**Client (****`config/.env.client`****)**

```ini
FAME_ADMISSION_PROFILE=direct               # client attaches over WebSocket (default)
FAME_DIRECT_ADMISSION_URL=wss://localhost/fame/v1/attach/ws/downstream
FAME_ADMISSION_TOKEN_URL=https://localhost/oauth/token
FAME_ADMISSION_CLIENT_ID=...
FAME_ADMISSION_CLIENT_SECRET=...
FAME_JWT_TRUSTED_ISSUER=https://oauth2-server
FAME_JWT_AUDIENCE=fame.fabric
SSL_CERT_FILE=./config/caddy/.../root.crt
```

---

## Running the example

```bash
make start       # Generate dev secrets, start Caddy, sentinel, OAuth2, and the HTTP‑connector agent
make run         # Run the Python client (still uses WebSocket to the sentinel)
make stop        # Tear down containers
```

> You can also inspect traffic with `make run-verbose` to print envelope metadata.

## Why `FAME_PUBLIC_URL` matters

Inside Docker Compose, service names become **network‑resolvable hostnames**. The agent must advertise a URL **the sentinel can reach** (not the host’s `localhost`). Setting `FAME_PUBLIC_URL=https://math-agent` ensures the sentinel’s callback goes to the agent’s container (via Caddy) rather than your host.

---

---

## About the custom node config

Previous examples rely on `dev_mode` configs that cover the common WebSocket path. This example uses a **custom YAML** to:

* enable the **`HttpListener`** on the agent,
* issue an **`HttpConnectionGrant`** with a Bearer token provider,
* configure the node’s **public URL** and security profile.

There’s no prebuilt preset for this combination, so you mount the config at `/etc/fame/fame-config.yml` (see `docker-compose.yml`).

---

## Caddy routing (what to look for)

In `config/Caddyfile`:

* `@sentinel_ws path /fame/v1/attach/ws/*` ➜ **sentinel‑internal:8000** (WebSocket attach)
* `@sentinel_http path /fame/v1/ingress/downstream/*` ➜ **sentinel‑internal:8000** (agent ➜ sentinel HTTP)
* `@math path /fame/v1/ingress/upstream` ➜ **math-agent-internal:8001** (sentinel ➜ agent HTTP callback)

This dual mapping is essential for the HTTP connector.

---

## Troubleshooting

* **Callback never arrives**

  * `FAME_PUBLIC_URL` not reachable from sentinel, or Caddy route missing `/fame/v1/ingress/upstream`.
  * Mismatch in `FAME_JWT_REVERSE_AUTH_AUDIENCE` between agent and sentinel.
* **401/403 on callback**

  * Wrong or missing `FAME_HMAC_SECRET`; the HMAC‑signed JWT cannot be verified.
  * Token `iss`/`aud` don’t match `FAME_JWT_TRUSTED_ISSUER` / `FAME_JWT_AUDIENCE`.
* **Agent attaches but no traffic**

  * One of the two HTTP legs is down. Verify both `/ingress/downstream` and `/ingress/upstream` paths in Caddy.
* **TLS errors**

  * Ensure every service trusts the Caddy internal CA via `SSL_CERT_FILE`.

---

## What you learn here

* How to operate the **HTTP connector** for agents in constrained networks.
* How to wire **reverse/callback authorization** using HMAC‑signed JWTs.
* How to use **`FAME_PUBLIC_URL`** to advertise correct service endpoints inside Docker.
* How to craft a **custom node config** when presets don’t cover advanced topologies.
* How to extend **Caddy** to handle both WebSocket and HTTP ingress for a mixed connector environment.
