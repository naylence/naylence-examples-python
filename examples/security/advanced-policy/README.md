# Advanced Security Policy — HTTP Policy Source (BSL)

Demonstrates **strict overlay security profile** with **X.509/SPIFFE workload certificates**, **sealed overlay encryption**, and **HTTP-based authorization policies**. This example extends the [advanced security example](../advanced/) by adding centralized policy management through an HTTP policy server.

---

## What's Different from the Advanced Example?

This example builds on the [advanced security example](../advanced/) with one key addition:

- **HTTP Authorization Policies**: Instead of loading policies from local files (`policy-localfile`), the sentinel fetches authorization policies from an HTTP endpoint (`policy-http`) served by a development auth policy server.

**Key differences:**

| Aspect                     | **Advanced Example**              | **Advanced-Policy Example (this)**    |
|----------------------------|-----------------------------------|---------------------------------------|
| Authorization Profile      | `policy-localfile`                | `policy-http`                         |
| Policy Storage             | Local YAML/JSON file              | HTTP endpoint with OAuth2 auth        |
| Additional Service         | None                              | Policy Server (port 8097)             |
| Policy Updates             | Requires file edit + restart      | Dynamic fetch with caching            |
| Production Readiness       | ✅ (file-based is production-ready) | ⚠️ (dev policy server, not for prod)  |

**Use this example to:**
- Learn how to implement centralized policy management
- Test dynamic policy updates without restarting nodes
- Understand OAuth2-secured policy endpoints
- Prototype policy-as-a-service architectures

> ⚠️ **Important:** The included auth-policy-server is for **development and testing only**. For production, use a secure, hardened policy management service.

---

## Overview

This example shows Naylence running in its **strictest security mode** with **centralized policy management**:

- **Cryptographic node identities**: Short-lived X.509/SPIFFE certificates
- **Federated admission**: Welcome service issues placement + attach tickets + CA grants
- **Certificate-based trust**: SPIFFE certs encode agent's physical path in the fabric
- **Dual validation**: Parent sentinels validate both attach ticket AND certificate
- **Sealed channels**: Overlay encryption ensures confidentiality across all hops

**Profiles in use:**

- Sentinel: `FAME_SECURITY_PROFILE=strict-overlay`, `FAME_ADMISSION_PROFILE=welcome`, `FAME_AUTHORIZATION_PROFILE=policy-http`
- Agent: `FAME_SECURITY_PROFILE=strict-overlay`, `FAME_ADMISSION_PROFILE=welcome`
- Client: `FAME_SECURITY_PROFILE=strict-overlay`, `FAME_ADMISSION_PROFILE=welcome`

**Authorization Policy Flow:**

1. **Sentinel startup**: Sentinel needs to fetch its authorization policy
2. **OAuth2 authentication**: Sentinel authenticates to the policy server using client credentials
3. **Policy fetch**: Sentinel retrieves policy from `https://policy/fame/v1/auth-policies/default`
4. **Caching**: Policy is cached with configurable TTL (default: 60 seconds)
5. **Dynamic updates**: Policy server supports file watching for live policy updates

> ⚠️ **Note:** This example requires the `naylence-advanced-security` package and the corresponding Docker image (`naylence/agent-sdk-adv-python:0.4.8`). These components are licensed under the **BSL** (Business Source License).

---

## Quick start

> Requirements: Docker + Docker Compose installed.

From this example folder:

```bash
make start       # 🔐 generates PKI + dev secrets, then brings up the stack (caddy, oauth2, welcome, ca, policy, sentinel, math-agent)
```

Run the sample client against the math agent (add/multiply/fib\_stream):

```bash
make run         # ▶️ executes client.py inside the example network
```

Shut down and clean up:

```bash
make stop        # ⏹ stop containers
make clean       # 🧹 remove generated .env files, PKI dir, caddy data, secrets
```

### See encryption in action

Use the verbose target to print every **envelope** as it travels through the fabric:

```bash
make run-verbose
```

You'll see signed and (when enabled) sealed envelopes printed to stdout, which is a handy way to verify overlay security end‑to‑end.

---

## What happens under the hood

1. **JWT** — The client/agent obtains a token from the OAuth2 dev server.
2. **Welcome** — Admission validates the token, issues:

   * Placement (which parent to attach to)
   * Attach ticket (short-lived capability)
3. **CA** — Agent node requests a SPIFFE/X.509 cert bound to its placement.
4. **Policy** — Sentinel fetches authorization policy from the policy server.
5. **Attach** — Agent node connects via TLS/WSS to the parent sentinel, presents:

   * Attach JWT ticket (authorization)
   * SPIFFE cert (identity + path binding)
6. **Validation** — Parent sentinel checks ticket *then* cert.
7. **Ack** — On success, overlay encryption and message signing are enabled with the agent's identity.

All of this is **fully automated** in this example.

---

## Services

| Service             | Port  | Description                                    |
|---------------------|-------|------------------------------------------------|
| Caddy               | 8443  | TLS termination with internal CA               |
| OAuth2 Server       | 8099  | Development token issuer                       |
| Welcome Service     | 8090  | Admission control (placement + tickets + CA)   |
| CA Service          | 8091  | SPIFFE X.509 certificate authority             |
| Policy Server       | 8097  | HTTP authorization policy endpoint             |
| Sentinel            | 8000  | Root node with strict overlay + HTTP policy    |
| Math Agent          | -     | Sample agent with add/multiply/fib operations  |

---

## Certificate lifecycle

There is no background "rotation."
All SPIFFE/X.509 certs are **short‑lived** (e.g., 24h).
When one expires, the agent repeats the Admission + CA flow to obtain a fresh cert.

---

## HTTP Policy Source Configuration

The sentinel is configured to use HTTP-based authorization policies:

```bash
# In config/.env.sentinel
FAME_AUTHORIZATION_PROFILE=policy-http
FAME_AUTH_POLICY_URL=https://policy/fame/v1/auth-policies/default
FAME_AUTH_POLICY_TIMEOUT_MS=5000
FAME_AUTH_POLICY_CACHE_TTL_MS=60000

# OAuth2 credentials for the policy server
FAME_AUTH_POLICY_TOKEN_URL=https://oauth2-server/oauth/token
FAME_AUTH_POLICY_CLIENT_ID=${DEV_CLIENT_ID}
FAME_AUTH_POLICY_CLIENT_SECRET=${DEV_CLIENT_SECRET}
FAME_AUTH_POLICY_AUDIENCE=fame.fabric
```

The policy server:
- Serves policies from `config/auth-policy.yaml`
- Requires OAuth2 JWT authentication (same credentials as fabric admission)
- Supports ETag-based caching (304 Not Modified)
- Watches the policy file for live updates (development mode)

---

## Troubleshooting

### Policy Server Authentication Errors

If you see JWT algorithm mismatch errors like:

```
"alg" (Algorithm) Header Parameter value not allowed
```

This usually means the OAuth2 server is using a different algorithm (e.g., EdDSA) than expected. The policy server is configured to accept RS256, ES256, and EdDSA algorithms by default.

### Sentinel Can't Fetch Policy

1. Check that the policy-internal service is running: `docker compose ps`
2. Verify the policy server logs: `docker compose logs policy-internal`
3. Ensure OAuth2 credentials are correctly generated: check `config/.env.policy`

### Certificate Issues

If you see certificate validation errors:

1. Regenerate PKI: `make clean && make init`
2. Ensure caddy-data volume is accessible
3. Check that `SSL_CERT_FILE` is set correctly in all `.env` files
