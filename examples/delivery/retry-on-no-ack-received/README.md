# Retry Example: At-Least-Once Delivery

This example demonstrates Naylence’s **at-least-once delivery policy** in action.
When a caller does not receive an acknowledgment (`ACK`) within a specified timeframe (defined by the sender retry policy), the message is **re-sent**.

As a result, the same message may be delivered multiple times. With this delivery policy, **idempotency or deduplication is the responsibility of the agent**.

---

## What’s inside

* **Sentinel** — central coordinator that manages routing.
* **MessageAgent** — receives messages and simulates dropped acknowledgments:

  * Internally, it hooks into low-level envelope events and randomly discards some ACKs using `LostAckSimulator` class:

    ```python
    class LostAckSimulator(NodeEventListener):
        
        def __init__(self):
            super().__init__()
            self._delivery_ack_counter = 0

        async def on_forward_upstream(
            self,
            node: NodeLike,
            envelope: FameEnvelope,
            context: FameDeliveryContext | None = None,
        ) -> FameEnvelope | None:
            if isinstance(envelope.frame, DeliveryAckFrame):
                self._delivery_ack_counter += 1
                if 0 < self._delivery_ack_counter % 3 < 3:
                    print(
                        "Simulating lost acknowledgment to envelope id",
                        envelope.frame.ref_id,
                    )
                    return None
            return envelope

    ```
  * ⚠️ This code is **only to simulate lost acknowledgments** for demonstration purposes. It is **not required** for retries in real systems.

  * From the agent’s perspective, this results in receiving the same message multiple times.
* **Client** — sends a simple `"Hello, World!"` message and waits for an acknowledgment.

Flow:

```
client ──▶ sentinel ──▶ message-agent
                ▲
                └── (ACKs may be dropped, forcing retries)
```

---

## Files

* `sentinel.py` — runs the sentinel.
* `message_agent.py` — agent that receives messages (and simulates ACK loss).
* `client.py` — sends a message.
* `docker-compose.yml` — orchestrates services.
* `config/.env.agent` — configures agent delivery mode.
* `config/.env.client` — configures client retry behavior.
* `Makefile` — convenience targets (`start`, `run`, `stop`, etc.).

---

## Quick start

> Requirements: Docker + Docker Compose installed.

1. **Start services**

```bash
make start
```

2. **Send a message (with retries)**

```bash
make run
```

👉 For more detailed visibility, you can also run:

```bash
make run-verbose
```

This will show the **actual envelopes** being sent by the client, making it easier to observe retries in action.

What happens:

* Client sends `"Hello, World!"`.
* MessageAgent receives it and prints it.
* Some ACKs are intentionally dropped → client retries.
* MessageAgent may log the same message multiple times.
* Eventually the client receives an acknowledgment.

3. **Stop everything**

```bash
make stop
```

---

## Expected output

Client:

```
Running client to send a message (with retries on no ACK received)...
Sending message to MessageAgent...
Acknowledgment received: type='DeliveryAck' ok=True code=None reason=None ref_id='dg7xsDbJGOzehjue'
```

Logs (`make run` shows them automatically):

```
message-agent-1  | Simulating lost acknowledgment to envelope id dg7xsDbJGOzehjue
message-agent-1  | MessageAgent received message: Hello, World!
message-agent-1  | Simulating lost acknowledgment to envelope id dg7xsDbJGOzehjue
message-agent-1  | MessageAgent received message: Hello, World!
message-agent-1  | MessageAgent received message: Hello, World!
```

---

## How it works

* **Retry policy** — if the client does not get an ACK in time, it resends the same message.
* **At-least-once delivery** — ensures eventual delivery, but may introduce duplicates.
* **Delivery profile configuration** — the delivery profile must be set to `FAME_DELIVERY_PROFILE=at-least-once` **on both the client and the agent side** for retries to work as intended.
* **Agent responsibility** — the framework does not deduplicate; your agent must handle duplicates if necessary.
* **Simulated ACK loss** — implemented only for demonstration. In real deployments, retries occur naturally due to network issues or node failures.

---

## Troubleshooting

* **Client hangs** → ensure sentinel is healthy (`docker ps` should show `sentinel` up).
* **No retries observed** → check that `FAME_DELIVERY_PROFILE=at-least-once` is set in both agent and client `.env` files.
* **Too many duplicates** → expected in this example, since ACKs are being intentionally dropped. In a real system, add deduplication logic in the agent.

---

## Key takeaway

With **at-least-once delivery**, messages are never silently lost, but they **may be delivered multiple times**. It’s up to the agent to ensure correct behavior in the presence of duplicates.
