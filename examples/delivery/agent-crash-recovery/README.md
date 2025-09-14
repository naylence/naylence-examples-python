# Crash Recovery: Agent Reprocessing Messages

This example demonstrates Naylence’s ability to **recover from agent crashes** and **automatically reprocess unhandled messages** — a core feature of the delivery system.

Normally, acknowledgments (`ACKs`) are issued *before* an agent finishes handling a message. If the agent crashes mid-processing, the framework ensures the message is not lost. With **at-least-once delivery mode** and a **durable store** enabled, the unprocessed message is preserved and retried when the agent restarts.

⚠️ **Important:** This example requires both:

* **At-least-once delivery mode** enabled via `FAME_DELIVERY_PROFILE=at-least-once`.
* A **durable storage backend** (e.g., SQLite). The default in-memory store will *not* persist messages across restarts.

Agent persistence is enabled in `config/.env.agent` using the following variables:

```
FAME_DELIVERY_PROFILE=at-least-once
FAME_STORAGE_PROFILE=encrypted-sqlite
FAME_STORAGE_MASTER_KEY=<your_master_key>
FAME_STORAGE_DB_DIRECTORY=./data/agent
```

---

## What’s inside

* **Sentinel** — coordination node that manages message routing.
* **MessageAgent** — stateful agent with a counter:

  * On each message, it increments the counter (persisted in agent state).
  * On **odd counts**, it simulates a crash (`sys.exit(1)`).
  * On **even counts**, it processes the message successfully.
* **Client** — sends a simple message (`"Hello, World!"`).

Flow:

```
client ──▶ sentinel ──▶ message-agent
```

* Odd count → agent crashes mid-processing → Docker Compose restarts it.
* Restart → agent resumes with counter incremented → reprocesses same message successfully.

---

## Files

* `sentinel.py` — starts the sentinel.
* `message_agent.py` — agent with counter + crash simulation.
* `client.py` — sends a message.
* `docker-compose.yml` — stack with auto-restart for the agent.
* `config/.env.agent` — configures delivery mode and durable storage.
* `Makefile` — convenience targets (`start`, `run`, `stop`, etc.).

---

## Quick start

> Requirements: Docker + Docker Compose installed.

1. **Start services**

```bash
make start
```

2. **Send a message (simulate crash & recovery)**

```bash
make run
```

What happens:

* Client sends `"Hello, World!"`.
* Agent receives message, increments counter → odd count.
* Agent simulates crash → container exits.
* Docker Compose restarts agent.
* Agent resumes with counter incremented → reprocesses the *same* message successfully.

Logs will show both the crash and the eventual successful processing.

3. **Stop everything**

```bash
make stop
```

---

## Expected output

Client:

```
Sending message to MessageAgent...
Acknowledgment received: DeliveryAck(ok=True, ...)
```

Logs (`make run` shows them automatically):

```
MessageAgent simulating crash while processing message...
... container restarts ...
MessageAgent processed message successfully: Hello, World!
```

---

## How it works

* **Pre-handle ACKs:** Naylence issues delivery acks before agent code executes. If the agent dies mid-task, the ack is not the end of the story.
* **At-least-once delivery:** Enabled via `FAME_DELIVERY_PROFILE=at-least-once`, ensures messages are retried if they weren’t fully processed.
* **Durable state:** Because the agent state (counter) and pending messages are in a persistent store, they survive restarts.
* **Recovery:** Upon restart, the agent automatically retries the unprocessed message. From the client’s perspective, delivery remains **at-least-once**.

---

## Troubleshooting

* **Agent doesn’t reprocess after crash** → check `config/.env.agent` to confirm both at-least-once delivery and durable storage are configured:

  ```
  FAME_DELIVERY_PROFILE=at-least-once
  FAME_STORAGE_PROFILE=encrypted-sqlite
  FAME_STORAGE_MASTER_KEY=<your_master_key>
  FAME_STORAGE_DB_DIRECTORY=./data/agent
  ```
* **Client hangs** → ensure sentinel is healthy (`docker ps` should show `sentinel` up).
* **Repeated crashes** → expected on odd counts; try sending multiple messages to see alternating crash/success behavior.
