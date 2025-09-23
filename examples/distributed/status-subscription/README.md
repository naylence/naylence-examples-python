# Status Subscription — A2A Task Updates Across the Fabric

This example shows how a client (or another agent) uses the **Agent‑to‑Agent (A2A) task interface** to **subscribe to live task updates** (status + artifacts) from a background task running on an agent.

---

Flow:

```
request: client ──▶ sentinel ──▶ status‑agent (start_task)
updates: client ◀─ sentinel ◀─ status‑agent (status/artifacts stream)
```

All messaging moves over the fabric; no REST servers or custom sockets.

---

> ⚠️ **Security note:** This demo is intentionally insecure for clarity. There is **no auth, TLS, or overlay security** enabled here. Later examples add secure admission, identities, and sealed channels.

---

> **For curious souls:** Naylence ships with FastAPI/Uvicorn under the hood but you’ll never need to see or configure it. All transport, routing, and addressing are handled by the fabric itself. No boilerplate servers, no route wiring, just `make start` and go.

---

## What you’ll learn

* Starting a background task with **`start_task(...)`**
* Subscribing to **status** and **artifact** updates via **`subscribe_to_task_updates(...)`**
* Emitting artifacts from an agent with **`update_task_artifact(...)`**
* Reading updates as a **stream** of `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent`

---

## Components

* **`status_agent.py`** — A `BackgroundTaskAgent` that simulates five work steps and emits progress artifacts.
* **`client.py`** — Starts a task, subscribes to its update stream, and prints both status and artifact messages.
* **`sentinel.py`** — Runs the sentinel (downstream attach URL served on `:8000`).
* **`docker-compose.yml`** — Starts **sentinel** and **status‑agent**; the client runs on the host.
* **`common.py`** — Declares the logical address `status@fame.fabric`.

**Logical address:** `status@fame.fabric`

---

## Quick start

> Requirements: Docker + Docker Compose installed.

From this example folder:

```bash
make start       # 🚀 bring up sentinel + status-agent
```

Run the sample client against the status agent:

```bash
make run         # ▶️ executes client.py
```

Shut down when done:

```bash
make stop        # ⏹ tear down containers
```

### See envelope traffic

Use the verbose target to print each **envelope** as it traverses the fabric:

```bash
make run-verbose
```

---

## Alternative: Docker Compose (manual)

1. **Start services**

```bash
docker compose up -d
```

This launches:

* **sentinel** on `localhost:8000`
* **status-agent** attached to the sentinel (via `FAME_DIRECT_ADMISSION_URL`)

2. **Run the client (host)**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

**Example output** (abridged):

```
[STATUS] TaskState.WORKING
[DATA ] step 1/5 complete
[DATA ] step 2/5 complete
[DATA ] step 3/5 complete
[DATA ] step 4/5 complete
[DATA ] step 5/5 complete
[STATUS] TaskState.FINISHED   # final state names may vary by SDK version
```

3. **Stop**

```bash
docker compose down --remove-orphans
```

---

## Standalone (no Compose)

Run each component in separate terminals with your local Python env:

**Terminal A — sentinel**

```bash
python sentinel.py
```

**Terminal B — agent**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python status_agent.py
```

**Terminal C — client**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

---

## How it works

### Agent

The agent subclasses `BackgroundTaskAgent` and periodically publishes progress artifacts while the background task runs:

```python
class StatusAgent(BackgroundTaskAgent):
    async def run_background_task(self, params: TaskSendParams):
        for i in range(1, 6):
            await asyncio.sleep(0.5)
            await self.update_task_artifact(
                params.id,
                Artifact(parts=[DataPart(data={"progress": f"step {i}/5 complete"})]),
            )
```

### Client

The client starts a task with a generated ID, then subscribes to the **same** ID’s update stream and discriminates the incoming events:

```python
async with FameFabric.create(root_config=configs.CLIENT_CONFIG):
    agent  = Agent.remote_by_address(AGENT_ADDR)
    task_id = generate_id()

    await agent.start_task(make_task_params(id=task_id))

    updates = await agent.subscribe_to_task_updates(make_task_params(id=task_id))
    async for evt in updates:
        if isinstance(evt, TaskStatusUpdateEvent):
            print(f"[STATUS] {evt.status.state}")
        elif isinstance(evt, TaskArtifactUpdateEvent):
            part = evt.artifact.parts[0]
            assert isinstance(part, DataPart)
            print(f"[DATA ] {part.data['progress']}")
```

Because the client, sentinel, and agent are separate services, **both** commands and updates travel across the fabric, but the code looks nearly identical to a single‑process setup.

---

## Troubleshooting

* **Client can’t connect** → Verify `FAME_DIRECT_ADMISSION_URL` (`localhost` from host; `sentinel` inside Compose network).
* **No updates appear** → Ensure the `task_id` used in `subscribe_to_task_updates` matches the one used in `start_task`.
* **Agent doesn’t attach** → Start **sentinel** first; check the env var in Compose.
* **Port in use** → Another process is using `8000`; change the Compose mapping or free the port.

---

## Next steps

* Emit richer artifacts (JSON progress, partial results, checkpoints, final payload).
* Demonstrate **client reconnection** and resubscribe to an in‑flight task.
* Combine with the **cancellable** example to add `cancel_task(...)` handling.
* Turn on **secure admission** (gated/overlay/strict‑overlay) without changing the app code.
