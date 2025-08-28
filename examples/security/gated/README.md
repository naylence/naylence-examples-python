# Gated Admission Example — OAuth2 Auth (No Overlay Encryption)

This example demonstrates how to protect a Naylence fabric using **OAuth2 client-credentials** admission with **security profiles** and **admission profiles**. A sentinel validates bearer tokens issued by a local OAuth2 server, gating access to agents and clients. Transport TLS is terminated by **Caddy**, and Naylence’s overlay encryption is **not enabled** in this example.

## Architecture diagram

![Architecture diagram](docs/diagram.png)

> ⚠️ **Security scope:** This example focuses only on **admission/auth** using OAuth2 tokens. TLS is handled by Caddy (reverse proxy). Naylence overlay encryption (message-level) is not used here. The included OAuth2 server is a **dev-only utility**; do not use it in production.

---

## What you’ll learn

* Running a Naylence **sentinel** with `security profile = gated`.
* Running a Naylence **agent** with `admission profile = direct` (connects to sentinel using a JWT).
* Running a Naylence **client** with `admission profile = direct`.
* Using a simple OAuth2 server to issue tokens for both agents and clients.
* Configuring security and admission with **profiles** instead of raw config.

---
## Why so many files?

You’ll notice this example has more moving parts than the earlier ones. In practice, we could have just checked demo credentials straight into git and everything would work out-of-the-box.

We deliberately chose not to do that. Even though these credentials would only ever be test values, checking secrets into version control is a bad security practice. To stay true to Naylence’s security philosophy, we instead generate unique credentials at setup time and distribute them into the appropriate .env.* files.

That decision adds a few extra files, but it also keeps the example aligned with real-world security hygiene:

- No static secrets in git

- Clear separation of roles (client, agent, sentinel, OAuth2 server)

- Automation via Make/generator script so you don’t have to manage values by hand

---
## Components

* **docker-compose.yml** — runs all long-lived services:

  * **caddy** — reverse proxy, terminates TLS with internal CA.
  * **oauth2-server** — dev-only OAuth2 provider (client credentials flow).
  * **sentinel** — Naylence fabric sentinel (`security profile = gated`).
  * **agent** — example agent (same RPC agent as in the distributed RPC example), configured with `admission profile = direct`.
* **client.py** — Python client, authenticates via OAuth2 and connects to the sentinel.
* **.env.client** — holds client configuration (token URL, client ID/secret, admission URL, CA cert).

**Profiles in use:**

* Sentinel: `FAME_SECURITY_PROFILE=gated`
* Agent: `FAME_ADMISSION_PROFILE=direct`
* Client: `FAME_ADMISSION_PROFILE=direct`

**Logical address**: `math@fame.fabric` (same as RPC example).

---

## Quick start

### Using Make (Recommended)

The easiest way to run this example is using the provided Makefile, which automates the entire workflow:

```bash
make
```

This single command will:
1. **Generate secrets** — Creates unique OAuth2 client credentials and populates all `.env.*` files
2. **Start services** — Launches Docker Compose with Caddy, OAuth2 server, sentinel, and math agent
3. **Run client** — Automatically executes the Python client to demonstrate the full workflow

**Why use Make?**
- **Automated setup**: No manual configuration of credentials or environment files
- **Consistent secrets**: Ensures all services use the same generated client ID and secret
- **One-command workflow**: Complete end-to-end demonstration with a single command
- **Error prevention**: Eliminates common setup mistakes like mismatched credentials

**Other Make targets:**
```bash
make init       # Generate secrets and .env files only
make up         # Start Docker services (includes init)
make run-client # Run the Python client
make down       # Stop Docker services
make clean      # Remove generated files and secrets
```

### Manual setup (Alternative)

If you prefer to run steps manually:

1. **Generate secrets and environment files**

```bash
python3 ../scripts/generate_dev_secrets.py --from-subdir
```

This creates:
- `.env.client`, `.env.agent`, `.env.oauth2-server`, `.env.sentinel` with unique credentials
- `../.secrets/oauth2-clients.json` with OAuth2 client configuration

2. **Start services**

```bash
docker compose up -d
```

This brings up Caddy (TLS), OAuth2 server, sentinel (gated), and the math agent (direct admission).

3. **Run the client**

```bash
python client.py
```

The client will:

* Load configuration from `.env.client` (via `python-dotenv`).
* Fetch a bearer token from the OAuth2 dev server (using client credentials).
* Connect to the sentinel at `wss://localhost/fame/v1/attach/ws/downstream`.
* Call the math agent’s RPCs.

### Example output

```
7
42
0 1 1 2 3 5 8 13 21 34
```

3. **Stop services**

```bash
docker compose down --remove-orphans
```

---

## Client env vars reference (.env.client)

Example `.env.client`:

```ini
FAME_ADMISSION_PROFILE=direct
FAME_DIRECT_ADMISSION_URL=wss://localhost/fame/v1/attach/ws/downstream
FAME_ADMISSION_TOKEN_URL=https://localhost/oauth/token
FAME_ADMISSION_CLIENT_ID=<YOUR_TEST_CLIENT_ID>
FAME_ADMISSION_CLIENT_SECRET=<YOUR_TEST_CLIENT_SECRET>
FAME_JWT_AUDIENCE=fame.fabric
SSL_CERT_FILE=./caddy/data/caddy/pki/authorities/local/root.crt
```

* **FAME\_ADMISSION\_PROFILE** — admission mode (`direct` means connect directly to sentinel using a JWT).
* **FAME\_DIRECT\_ADMISSION\_URL** — sentinel attach URL (through Caddy).
* **FAME\_ADMISSION\_TOKEN\_URL** — OAuth2 server token endpoint.
* **FAME\_ADMISSION\_CLIENT\_ID/SECRET** — OAuth2 client credentials.
* **FAME\_JWT\_AUDIENCE** — must match sentinel’s trusted audience.
* **SSL\_CERT\_FILE** — path to Caddy’s internal root CA cert, so Python trusts TLS.

---

## Agent env vars reference (.env.agent)

The agent uses the **same variables as the client**, but since it runs inside Docker Compose, the values differ slightly:

```ini
SSL_CERT_FILE=/work/caddy/data/caddy/pki/authorities/local/root.crt
FAME_DIRECT_ADMISSION_URL=wss://sentinel/fame/v1/attach/ws/downstream
FAME_ADMISSION_PROFILE=direct
FAME_ADMISSION_TOKEN_URL=https://oauth2-server/oauth/token
FAME_ADMISSION_CLIENT_ID=<YOUR_TEST_CLIENT_ID>
FAME_ADMISSION_CLIENT_SECRET=<YOUR_TEST_CLIENT_SECRET>
FAME_JWT_AUDIENCE=fame.fabric
```

---

## Sentinel env vars reference (.env.sentinel)

The sentinel does not connect upstream, but it enforces gated security:

```ini
SSL_CERT_FILE=/work/caddy/data/caddy/pki/authorities/local/root.crt
FAME_SECURITY_PROFILE=gated
FAME_JWT_TRUSTED_ISSUER=https://oauth2-server
FAME_JWT_AUDIENCE=fame.fabric
```

---

## Notes

* The OAuth2 server included here is for **development only**. In production, use a real identity provider (Keycloak, Auth0, Okta, etc.).
* Always run Caddy (or another reverse proxy) for TLS termination; Naylence does **not** provide TLS itself.
* Overlay encryption (end-to-end message security) is a separate layer, demonstrated in later examples.

---

## Troubleshooting

* **401 Unauthorized** — check that client/agent ID & secret match OAuth2 server config; verify `FAME_JWT_AUDIENCE` matches sentinel’s config.
* **TLS errors** — confirm `SSL_CERT_FILE` points to Caddy’s root CA cert (`./caddy/data/caddy/pki/authorities/local/root.crt`).
* **WS connection refused** — ensure Docker Compose is up; Caddy listens on `443`.

---

This example demonstrates **admission gating with OAuth2** using **profiles**: sentinel in `gated` mode, client and agent in `direct` mode. TLS remains at the proxy; overlay encryption is left for later examples.
