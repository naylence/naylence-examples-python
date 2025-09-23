# Distributed Cancellable Agent — A2A Tasks & Cancellation

This example demonstrates **Agent‑to‑Agent (A2A) task APIs** in a **distributed** topology. A client starts a long‑running task on an agent, subscribes to task updates (status + artifacts), reacts to progress, and then **cancels** the task mid‑flight.

---
Flow:
```
request: client ──▶ sentinel ──▶ cancellable-agent
reply:   client ◀─ sentinel ◀─ cancellable-agent
updates: client ◀─ sentinel ◀─ cancellable-agent (status/artifacts)
```

---
> ⚠️ **Security note:** This demo is intentionally insecure for clarity. There is **no auth, TLS, or overlay security** enabled here. Later examples will layer in secure admission, identities, and sealed channels.

---
> **For curious souls:** Naylence ships with FastAPI/Uvicorn under the hood but you’ll never need to see or configure it. All transport, routing, and addressing are handled by the fabric itself. No boilerplate servers, no route wiring, just `make start` and go.
---

## What you’ll learn

* Starting long‑running tasks with **`start_task(...)`**
* Receiving live **status** and **artifact** updates via **`subscribe_to_task_updates(...)`**
* Updating artifacts from the agent using **`update_task_artifact(...)`**
* Querying task state with **`get_task_state(...)`**
* Canceling work with **`cancel_task(...)`**

---

## Components

* **cancellable\_agent.py** — Implements a `BackgroundTaskAgent` that simulates work in steps, emits progress artifacts, and stops when canceled.
* **client.py** — Starts a task, subscribes to updates, prints progress, and cancels after a threshold.
* **sentinel.py** — Runs the sentinel (downstream admission point at `:8000`).
* **docker-compose.yml** — Brings up **sentinel** and **cancellable-agent**; you run the client from the host.
* **common.py** — Holds the logical address `cancellable@fame.fabric`.

---

## Quick start

> Requirements: Docker + Docker Compose installed.

From this example folder:

```bash
make start       # 🚀 brings up the stack (sentinel + cancellable-agent)
```

Run the sample client against the cancellable agent:

```bash
make run         # ▶️ executes client.py
```

Shut down when done:

```bash
make stop        # ⏹ stop containers
```

### See envelope traffic

Use the verbose target to print every **envelope** as it travels through the fabric:

```bash
make run-verbose
```

---

## Alternative: Quick start (Docker Compose)

1. **Start services**

```bash
docker compose up -d
```

This starts:

* **sentinel** on `localhost:8000`
* **cancellable-agent** connected to the sentinel

2. **Run the client (host)**

```bash
make run
```

or 

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

### Example output

```
[STATUS] TaskState.WORKING
[DATA ] progress: 0.1
[DATA ] progress: 0.2
[DATA ] progress: 0.3
[DATA ] progress: 0.4
[DATA ] progress: 0.5
Canceling task iuqSvFy19cUxswS
[STATUS] TaskState.CANCELED
```

3. **Stop**

```bash
docker compose down --remove-orphans
```

---

## Standalone (no Compose)

Use your local Python env to run each component in separate terminals:

**Terminal A — sentinel**

```bash
python sentinel.py
```

**Terminal B — agent**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python cancellable_agent.py
```

**Terminal C — client**

```bash
export FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream"
python client.py
```

---

## How it works

### Agent

* Subclass: **`BackgroundTaskAgent`**
* Entry point: **`run_background_task(params: TaskSendParams)`** — runs asynchronously in the background.

**Minimal agent loop**

```python
from naylence.agent import BackgroundTaskAgent, TaskState
from naylence.agent import Artifact, DataPart
import asyncio

class CancellableAgent(BackgroundTaskAgent):
    async def run_background_task(self, params):
        steps = params.payload.get("steps", 10)
        for i in range(steps):
            # 1) honor cancellation
            if await self.get_task_state(params.id) == TaskState.CANCELED:
                return  # stop quietly

            # 2) compute progress
            progress = (i + 1) / steps

            # 3) emit progress artifact
            await self.update_task_artifact(
                id=params.id,
                artifact=Artifact(parts=[DataPart(data={"progress": progress})]),
            )

            # 4) simulate work
            await asyncio.sleep(0.5)
```

### Client

**Start → subscribe → cancel**

```python
async def main():
    async with FameFabric.create(root_config=CLIENT_CONFIG):
        agent = Agent.remote_by_address(AGENT_ADDR)
        task_id = generate_id()

        await agent.start_task(make_task_params(id=task_id))

        updates = await agent.subscribe_to_task_updates(make_task_params(id=task_id))

        async for evt in updates:
            if isinstance(evt, TaskStatusUpdateEvent):
                print(f"[STATUS] {evt.status.state}")
            elif isinstance(evt, TaskArtifactUpdateEvent):
                part = evt.artifact.parts[0]
                assert isinstance(part, DataPart)
                progress = part.data["progress"]
                print(f"[DATA ] progress: {progress}")
                if progress >= 0.5:
                    print(f"Canceling task {task_id}")
                    await agent.cancel_task(TaskIdParams(id=task_id))
```

Because the client, sentinel, and agent are separate services, all commands and update streams travel across the fabric — but the code looks almost identical to the single‑process version.

---

## Troubleshooting

* **Client can’t connect** → Ensure `FAME_DIRECT_ADMISSION_URL` points to the sentinel you’re using (`localhost` from host; `sentinel` in Compose).
* **Agent doesn’t attach** → Start the **sentinel** first; check the env var in Compose.
* **No updates appear** → Confirm you subscribed with the same `task_id` you used to start the task.
* **Port in use** → Another process is using `8000`; change the Compose mapping or free the port.

---

## Next steps

* Replace the dummy loop with real long‑running work (downloads, ETL, training, etc.).
* Add **checkpoint artifacts** and **final result** artifacts.
* Demonstrate **client reconnection** and resubscribing to in‑flight tasks.
* Add **secure admission** and **overlay encryption** to the same example.

---

This example highlights the full A2A lifecycle — **start → stream updates → cancel** — and, by contrast, helps you appreciate how simple the one‑shot `run_task(...)` API is in earlier examples.
