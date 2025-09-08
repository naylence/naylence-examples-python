# OpenTelemetry Example — Tracing with Explicit Configs

This example demonstrates how to integrate **OpenTelemetry** into a Naylence fabric. Unlike previous examples that relied on `dev_mode` configs, here we use **explicit configuration files** for the sentinel, agent, and client. This allows us to configure OpenTelemetry emitters alongside security and admission profiles.

Telemetry data is exported to an **OpenTelemetry Collector**, which forwards it to **Jaeger** for visualization. Authentication for telemetry export uses the same OAuth2 provider as admission, and the collector itself is protected by OIDC.

---

## What you’ll learn

* Running a Naylence **sentinel**, **agent**, and **client** with explicit YAML configs (`sentinel-config.yml`, `agent-config.yml`, `client-config.yml`).
* Configuring **OpenTelemetry emitters** for each node.
* Exporting telemetry traces to an **OTel Collector** and visualizing them in **Jaeger**.
* Using OAuth2 tokens not only for admission but also for authenticating telemetry exports.
* How to configure the OpenTelemetry collector itself with OIDC protection.

---

## Components

* **docker-compose.yml** — orchestrates services:

  * **caddy** — reverse proxy, terminates TLS with internal CA.
  * **oauth2-server** — dev-only OAuth2 provider (client credentials flow).
  * **otel-collector** — receives traces, enforces OIDC, and exports them to Jaeger + debug output.
  * **jaeger** — UI for viewing traces.
  * **sentinel** — Naylence sentinel configured via `sentinel-config.yml`.
  * **math-agent** — RPC agent configured via `agent-config.yml`.
  * **client** — Python client configured via `client-config.yml` and `.env.client`.

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
2. Start Caddy, OAuth2 server, OTel collector, Jaeger, sentinel, and math agent.
3. Run the Python client.

### Example client output

```
7
42
0 1 1 2 3 5 8 13 21 34
```

ℹ️ Traces will be available in **Jaeger UI** at [http://localhost:16686](http://localhost:16686).

---

## Telemetry Configuration

### Client/Agent/Sentinel (YAML config)

Each node explicitly declares a telemetry emitter. Example:

```yaml
telemetry:
  type: OpenTelemetryTraceEmitter
  service_name: naylence-telemetry
  endpoint: "${env:FAME_TELEMETRY_OTLP_ENDPOINT:}"
  auth:
    type: BearerTokenHeaderAuth
    token_provider:
      type: OAuth2ClientCredentialsTokenProvider
      token_url: ${env:FAME_TELEMETRY_TOKEN_URL}
      client_id: ${env:FAME_TELEMETRY_CLIENT_ID}
      client_secret: ${env:FAME_TELEMETRY_CLIENT_SECRET}
      scopes:
        - node.connect
      audience: ${env:FAME_TELEMETRY_JWT_AUDIENCE}
```

This config ensures that telemetry spans are exported via OTLP to the collector, with OAuth2 client-credentials used to authenticate.

---

### OpenTelemetry Collector (server side)

The collector itself enforces OIDC authorization on incoming telemetry:

```yaml
extensions:
  oidc:
    issuer_url: https://oauth2-server
    audience: "fame.fabric"

# OpenTelemetry Collector configuration for integration tests
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
        auth:
          authenticator: oidc
```

This configuration ensures only authenticated nodes can push telemetry data into the collector.

---

## Env vars reference

Example `.env.agent`:

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

FAME_TELEMETRY_OTLP_ENDPOINT=https://otel-collector/v1/traces
FAME_TELEMETRY_TOKEN_URL=https://oauth2-server/oauth/token
FAME_TELEMETRY_CLIENT_ID=<YOUR_TEST_CLIENT_ID>
FAME_TELEMETRY_CLIENT_SECRET=<YOUR_TEST_CLIENT_SECRET>
FAME_TELEMETRY_JWT_AUDIENCE=fame.fabric

OTEL_EXPORTER_OTLP_CERTIFICATE=/work/config/caddy/data/caddy/pki/authorities/local/root.crt
```

---

## Notes

* This example shows how to integrate Naylence with **industry-standard observability tools**.

* The OTel collector here is dev-only; production setups should use hardened collector deployments.

* Jaeger is optional, you can configure other exporters (Grafana Tempo, Datadog, etc.).

* Securing Jaeger itself (e.g., authentication, access control) is **out of scope** for this example.

* The OAuth2 server included here is for **development purposes only**. In production, use a real identity provider (Keycloak, Auth0, Okta, etc.).
