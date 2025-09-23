# Security Examples with Naylence

This folder collects **distributed security setups** in Naylence.

All examples here run with **Docker Compose** and demonstrate how different **security models** work in the fabric. Unlike the [distributed examples](../distributed), these focus specifically on **admission, authentication, and encryption profiles**.

You do **not** need to run or configure your own HTTP servers or endpoints. Naylence provides the runtime, connectors, and routing out of the box. REST/HTTP appears here only in the special **HTTP Connector** case.

---

## Security Profiles Demonstrated

- **gated/** — Sentinel runs in **gated** profile. Admission is handled via OAuth2 bearer tokens. TLS termination is handled by Caddy. No overlay encryption.
- **overlay/** — Sentinel runs in **overlay** profile. Adds **envelope signing** and public key exchange between nodes for tamper‑evidence and authenticity.
- **advanced/** — Sentinel + agents run in **strict‑overlay** profile. Adds **federated identity** (Welcome service + CA) and **SPIFFE/X.509 certs**. Requires the advanced BSL package.
- **stickiness/** — Builds on strict‑overlay with **channel encryption** and **sticky load‑balancing**. Clients are pinned to a replica for the lifetime of a secure channel.
- **http-connector/** — Demonstrates replacing the default **WebSocket connectors** with **HTTP connectors**. Uses a downstream (agent ➜ sentinel) and upstream (sentinel ➜ agent callback) link to emulate full‑duplex. Requires special security config: overlay‑callback and reverse HMAC‑JWT auth.

---

## What “Security” Means Here

- **Admission control** — How a node is authorized to join the fabric (open, gated, welcome service, etc.).
- **Identity** — How nodes prove who they are (OAuth2 bearer tokens, public keys, SPIFFE/X.509 certs).
- **Encryption** — How messages are protected:
  - *Transport TLS* (via Caddy)
  - *Envelope signing* (overlay profile)
  - *Channel encryption* (strict‑overlay profile)
  - *Sealed encryption* (strict‑overlay profile)
- **Profiles** — Set via `FAME_SECURITY_PROFILE` and `FAME_ADMISSION_PROFILE` in `.env.*` files.

---

## Running the Examples

Each directory contains its own `Makefile` with the following common targets:

```bash
make start       # generate secrets (if needed) + start docker-compose
make run         # run the Python client (talks to the math agent)
make run-verbose # run client with FAME_SHOW_ENVELOPES=true to inspect envelopes
make stop        # stop all services
make clean       # remove generated .env files, secrets, certs
```

All examples spin up:
- **caddy** — reverse proxy, TLS termination
- **oauth2-server** — dev OAuth2 provider (for admission tokens)
- **sentinel** — Naylence sentinel node with chosen security profile
- **math-agent** — sample RPC agent
- (sometimes) **welcome** and **ca** — advanced admission + cert authority services

---

## Quick Map of Examples

| Example          | Admission Profile | Security Profile    | Special Features |
|------------------|------------------|---------------------|------------------|
| gated            | direct           | gated               | OAuth2 auth only, no overlay |
| overlay          | direct           | overlay             | Envelope signing, public key exchange |
| advanced         | welcome          | strict‑overlay      | SPIFFE/X.509 certs, admission tickets |
| stickiness       | welcome          | strict‑overlay      | Channel encryption + sticky LB |
| http-connector   | direct-http      | overlay‑callback    | HTTP connectors, reverse HMAC‑JWT auth |

---

## Special Notes

- **Dev only**: OAuth2 server, Welcome, and CA here are dev‑only utilities. Replace with your own IdP/CA in production.
- **Overlay vs TLS**: TLS protects the channel; overlay signing adds cryptographic provenance at the envelope level.
- **Advanced & Stickiness**: Require the `naylence-advanced-security` BSL package and advanced Docker images.
- **HTTP Connector**: The only example where agents don’t use WebSockets. Useful in restricted environments.

---

> **Tip:** To explore security internals, run with `make run-verbose` and inspect the `sec.sig` and `sec.enc` fields inside printed envelopes. These show which profile (signing, sealing, channel) is in effect.
