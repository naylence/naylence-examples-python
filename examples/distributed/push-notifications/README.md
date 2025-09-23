# Distributed Push Notifications Example

This example demonstrates how to use the Naylence Agent SDK to implement a **push‑notification** pattern via callback rather than streaming. It consists of:

* A **Fame router** (`sentinel.py`) that routes all messages over WebSocket
* A **PushSender** agent (`push_sender.py`) that runs background tasks and pushes notifications to registered endpoints
* A **PushReceiver** agent (`push_receiver.py`) that:

  * Registers its own endpoint with the sender
  * Receives and prints notifications via a callback handler
* A **client script** (`client.py`) that drives the receiver
* A **shared config** (`common.py`) defining addresses and FameFabric settings

---

## Prerequisites

* **Python 3.12+**
* **Naylence Agent SDK** installed (editable or via PyPI):

  ```bash
  pip install -e .
  ```
* **FastAPI** and **Uvicorn** for the router:

  ```bash
  pip install fastapi uvicorn
  ```
* No external API keys are required for this demo.

---
> ⚠️ **Security note:** This demo is intentionally insecure for clarity. There is **no auth, TLS, or overlay security** enabled here. Later examples will layer in secure admission, identities, and sealed channels.

---
> **For curious souls:** Naylence ships with FastAPI/Uvicorn under the hood but you’ll never need to see or configure it. All transport, routing, and addressing are handled by the fabric itself. No boilerplate servers, no route wiring, just `make start` and go.
---

## Directory Layout

```
examples/distributed_push_notifications/
├── common.py            # Addresses & FameFabric configs
├── sentinel.py          # Fame router (FastAPI + WS attach)
├── push_sender.py       # PushSender agent (BackgroundTaskAgent)
├── push_receiver.py     # PushReceiver agent (BackgroundTaskAgent)
└── client.py            # Simple client to start the receiver
```

---

## Configuration (`common.py`)

* **RECEIVER\_AGENT\_ADDR** — Logical address where `PushReceiver` is served (`"receiver@fame.fabric"`).
* **SENDER\_AGENT\_ADDR** — Logical address for `PushSender` (`"sender@fame.fabric"`).
* **client\_config** — FameFabric settings for the client (dev mode, WS URL).
* **agent\_config** — FameFabric settings for both agents (dev mode, WS URL).
* **sentinel\_config** — FameFabric router settings (dev, WS attach, NoopAuthorizer).

---

## How It Works

1. **Start the Fame router**

   ```bash
   uvicorn sentinel:app --host 0.0.0.0 --port 8000
   ```

   This spins up a FastAPI server with the WS attach endpoint at `/fame/ws/downstream`.

2. **Launch the PushSender agent**

   ```bash
   python push_sender.py
   ```

   * Uses `BackgroundTaskAgent.aserve()` to serve at `"sender@fame.fabric"`.
   * Stores incoming `TaskPushNotificationConfig` in an internal dict.
   * When its `run_background_task` is invoked, it loops \~10 times, sending JSON notifications to the registered endpoint using `FameFabric.current().send_json(url, payload)`.

3. **Launch the PushReceiver agent**

   ```bash
   python push_receiver.py
   ```

   * Serves at `"receiver@fame.fabric"` via `BackgroundTaskAgent.aserve()`.
   * Its `run_background_task` does:

     1. Generate a new `task_id`.
     2. **RPC** to `PushSender.register_push_endpoint(...)`, passing a `TaskPushNotificationConfig` with its own address.
     3. **RPC** to `PushSender.run_task(id=task_id)` which starts the sender’s background loop.
   * Implements `on_message(self, message)` to print each incoming push notification.

4. **Run the client**

   ```bash
   python client.py
   ```

   * Creates a FameFabric context.
   * Obtains a proxy to `PushReceiver` and calls `run_task()` to enqueue its background job.
   * As the job runs, you’ll see in the **receiver** console:

     ```text
     PushReceiver running task: <random-id>
     PushSender configured endpoint for task <random-id>
     PushSender running task <random-id>
     PushSender sent notification {'task_id': ..., 'message': 'Notification #1'}
     PushReceiver got notification: {'task_id': ..., 'message': 'Notification #1'}
     ...
     PushSender sent notification {'task_id': ..., 'message': 'Notification #10'}
     PushReceiver got notification: {'task_id': ..., 'message': 'Notification #10'}
     PushSender completed task <random-id>
     PushReceiver completed task: <original-task-id>
     ```

---

## Key Concepts Demonstrated

* **Callback‐style notifications** via `send_json` and a custom `on_message`
* **Decoupled agents**: sender knows nothing about the receiver beyond its address
* **BackgroundTaskAgent**: leveraging long‐running tasks with status updates
* **FameFabric routing**: WebSocket attach, JSON frame delivery
* **RPC + push combo**: using one A2A call to configure, another to start

---

## Troubleshooting

* **No notifications?** Ensure both agents use the *same* `SENDER_AGENT_ADDR` in `common.py`.
* **Router errors?** Check that `sentinel.py` is running and reachable at `ws://localhost:8000/fame/downstream`.
* **Timeouts in client?** Verify the receiver is up before running the client, or add a retry.

---

Feel free to customize the number of notifications, throttle interval, or extend `register_push_endpoint` to support filters or formats. This example serves as a template for any callback‐based, cross‐agent notification workflow.
