# Advanced Security — Strict Overlay (BSL)

This example shows Naylence running in its **strictest security mode**:
agents join the fabric only after passing through a full **admission + identity** flow,
with **SPIFFE/X.509 workload certificates** and **sealed overlay encryption**.

---

## Why this matters

* **Agent node identities** are cryptographic, short-lived, and automatically issued.
* **Admission service** decides *where* each agent node belongs and issues scoped attach tickets.
* **Certificates** encode the agent’s physical path in the fabric.
* **Parent sentinels** validate both the attach ticket *and* the cert before finalizing the attach.
* **Overlay encryption** ensures agent-to-agent  confidentiality and authenticity across hops.

This is the **enterprise zero-trust profile** of Naylence, available under the **BSL license**.
The open-source core already provides strong EdDSA-based overlay signing — this example
adds a federated identity and admission layer for cross-org and regulated deployments.

> ⚠️ **Note:** This example requires the `naylence-advanced-security` package and the
> corresponding Docker image (`naylence/agent-sdk-adv-python`). These components
> are licensed under the **BSL**.

---

## Quick start

> Requirements: Docker + Docker Compose installed.

From this example folder:

```bash
make start       # 🔐 generates PKI + dev secrets, then brings up the stack (caddy, oauth2, welcome, ca, sentinel, math-agent)
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

You’ll see signed and (when enabled) sealed envelopes printed to stdout, which is a handy way to verify overlay security end‑to‑end.

---

## What happens under the hood

1. **JWT** — The client/agent obtains a token from the OAuth2 dev server.
2. **Welcome** — Admission validates the token, issues:

   * Placement (which parent to attach to)
   * Attach ticket (short-lived capability)
3. **CA** — Agent node requests a SPIFFE/X.509 cert bound to its placement.
4. **Attach** — Agent node connects via TLS/WSS to the parent sentinel, presents:

   * Attach JWT ticket (authorization)
   * SPIFFE cert (identity + path binding)
5. **Validation** — Parent sentinel checks ticket *then* cert.
6. **Ack** — On success, overlay encryption and message signing are enabled with the agent’s identity.

All of this is **fully automated** in this example.

---

## Certificate lifecycle

There is no background “rotation.”
All SPIFFE/X.509 certs are **short‑lived** (e.g., 24h).
When one expires, the agent repeats the Admission + CA flow to obtain a fresh cert.

---

## Sample envelope (verbose mode)

A **data frame** envelope printed by `make run-verbose` might look like this:

```json
{
  "version": "1.0",
  "id": "mu2l8LmB6bvJAiL",
  "sid": "6KbaPqxYq8p3hjDaUw3YBH",
  "traceId": "Or9bha2d6tDb2yC",
  "to": "math@fame.fabric",
  "replyTo": "rpc-N7GImNdeVMvRMQo@/Cb8WVCC4ML5RsFM/9gxwoGeeBBSR3Oh",
  "rtype": 2,
  "corrId": "3f1kkiuHVcbiTT3",
  "seqId": 0,
  "flowFlags": 0,
  "frame": {
    "type": "Data",
    "codec": "b64",
    "payload": "wOigrL848iSgv8qfUdntQTwMzEVRYBSTQLqY7Vwui7lJMHm2Akuze3gL5jBH0GKqw99canUn1EsrA6vss51OGgFyDTLbwz5rljcATB9TA8X7wERTvtUa8QWsaMfC5LFYJuc/nZsRqX7pZAXC3FWFvgwAUw==",
    "pd": "4Fg9MfgDCY09YqN0ep7Ntx"
  },
  "ts": "2025-08-29T23:56:10.366Z",
  "sec": {
    "sig": {
      "kid": "xAhddeRwu2UvuJr",
      "val": "IyaOG4hMLuafFAv8Sd77HUb1PhKobN0lCOOu7Qpa-y59QFH_3BMO98OPbKalzoKoJEsH9tkJimA9P7c4YQ2LDA"
    },
    "enc": {
      "alg": "chacha20-poly1305-channel",
      "kid": "auto-math@fame.fabric-7snnHCFG1FA5UGV",
      "val": "07d951bb68c86085f50e57b9"
    }
  }
}
```

### What to look for (high‑level)

* `id`, `seqId`, `traceId`, `corrId`, `flowId` — delivery and tracing metadata.
* `to` — fabric destination (agent address).
* `frame` — the **content**: here a `Data` frame with base64 payload and optional per‑frame metadata `pd`.
* `ts` — send timestamp.
* `sec.sig` — **envelope signature** (EdDSA) with key id `kid`; guarantees integrity and authenticity end‑to‑end.
* `sec.enc` — **overlay encryption** details when sealing is on (algorithm, sender key id, short auth tag / nonce material). Confirms confidentiality on top of channel TLS.
* `payload` — **encrypted data payload**

In strict overlay, parents validate the **attach ticket**, then the **SPIFFE/X.509 cert** (including placement binding). After ack, sealed channels use these identities for authenticated encryption across hops.

---

---

## Notes

* This demo uses a **dev OAuth2 server** and Caddy TLS termination for convenience.
* Do **not** use this setup in production; integrate with your real IdP and secure CA.
* Example is provided for evaluation; production onboarding requires professional services.
