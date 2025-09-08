# Overlay Security Example — Envelope Signing (Public Key Exchange)

This example demonstrates how to protect a Naylence fabric using the **overlay security profile**, which enables **envelope signing** for message integrity and authenticity. Unlike the *gated* example, overlay security establishes cryptographic trust between nodes themselves, rather than relying only on bearer tokens.

When a node attaches to a parent node, they **exchange raw public keys**. These keys are then used to:

* Sign and verify envelopes (messages in transit).
* Ensure provenance via **SIDs** (source node fingerprints).
* Provide tamper-evidence, non-repudiation, and audit trails.

> ⚠️ **Note:** Public key exchange in this example does **not** use X.509 certificates. Certificates are supported only in the **advanced security package**.

---

## What you’ll learn

* Running a Naylence **sentinel** with `security profile = overlay`.
* Running a Naylence **agent** with `admission profile = direct`.
* Running a Naylence **client** with `admission profile = direct`.
* How envelope signing secures communications beyond simple TLS.
* The difference between `gated` and `overlay` profiles:

  * **gated** = admission/auth with OAuth2 tokens
  * **overlay** = envelope-level security with public key signing

---

## Components

* **docker-compose.yml** — runs all long-lived services:

  * **caddy** — reverse proxy, terminates TLS with internal CA.
  * **oauth2-server** — dev-only OAuth2 provider (for admission tokens).
  * **sentinel** — Naylence fabric sentinel (`security profile = overlay`).
  * **math-agent** — example RPC agent, configured with `admission profile = direct`.
* **client.py** — Python client, authenticates via OAuth2 and connects to sentinel.
* **.env.**\* — environment configs for each role (client, agent, sentinel, OAuth2 server).

**Profiles in use:**

* Sentinel: `FAME_SECURITY_PROFILE=overlay`
* Agent: `FAME_ADMISSION_PROFILE=direct`
* Client: `FAME_ADMISSION_PROFILE=direct`

---

## Quick start

### Using Make

```bash
make
```

This will:

1. Generate secrets and environment files.
2. Start Caddy, OAuth2 server, sentinel (overlay), and math agent.
3. Run the Python client with overlay signing enabled.

### Example client output

```
7
42
0 1 1 2 3 5 8 13 21 34
```

Run with verbose output to see **signed envelopes**:

```bash
make run-verbose
```

---

## Env vars reference

Example `.env.agent` (inside Docker):

```ini
SSL_CERT_FILE=/work/config/caddy/data/caddy/pki/authorities/local/root.crt
FAME_SECURITY_PROFILE=overlay
FAME_ADMISSION_PROFILE=direct
FAME_DIRECT_ADMISSION_URL=wss://sentinel/fame/v1/attach/ws/downstream
FAME_ADMISSION_TOKEN_URL=https://oauth2-server/oauth/token
FAME_ADMISSION_CLIENT_ID=<YOUR_TEST_CLIENT_ID>
FAME_ADMISSION_CLIENT_SECRET=<YOUR_TEST_CLIENT_SECRET>
FAME_JWT_TRUSTED_ISSUER=https://oauth2-server
FAME_JWT_AUDIENCE=fame.fabric
```

* **FAME\_SECURITY\_PROFILE=overlay** — enables overlay security (envelope signing).
* **FAME\_ADMISSION\_PROFILE=direct** — node connects to sentinel directly with token.
* **Public keys are exchanged** during node attach — used for signing/verification.

---

## Notes

* Overlay security ensures **message-level integrity**, even if TLS is broken.
* This example still uses OAuth2 for admission, but trust between nodes is enforced cryptographically at the envelope layer.
* Certificates (X.509 / SPIFFE identities) require the **advanced security package**.
