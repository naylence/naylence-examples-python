# Chat Agent (LLM) Example — Stateful Conversations over the Fabric

This example builds a small **chat agent** that maintains per‑conversation history and talks to an LLM via the OpenAI API. A local **dev‑mode sentinel** coordinates routing; the client attaches to it and drives an interactive REPL.

```
client  →  sentinel  →  chat@fame.fabric (ChatAgent)
```

---

## What this shows

* **Per‑conversation state** using `start_task` / `run_turn` / `end_conversation`.
* **In‑process dev fabric** with `dev_mode` sentinel and an agent connected over WebSocket.
* **LLM callout** via the OpenAI Chat Completions API (model configurable).
* **Clean message loop**: user input → agent turn → assistant reply, with a bounded history window.

---

## Files

* **`docker-compose.yml`** — starts a sentinel on **8000** and the chat agent container.
* **`sentinel.py`** — runs a dev‑mode sentinel (`run_sentinel(log_level="info")`).
* **`chat_agent.py`** — the `ChatAgent` implementation with conversation memory.
* **`client.py`** — attaches to the sentinel, starts a conversation, and runs a REPL.
* **`common.py`** — shared bits: `AGENT_ADDR = "chat@fame.fabric"`, OpenAI helper, model name.
* **`Dockerfile`** — extends the SDK image and installs the `openai` package.
* **`Makefile`** — `start`, `run`, `run-verbose`, `stop` targets.

---

## How it works (flow)

1. **Sentinel** starts and listens on `ws://localhost:8000`.
2. **ChatAgent** attaches to the sentinel using `FAME_DIRECT_ADMISSION_URL=ws://sentinel:8000/fame/v1/attach/ws/downstream`.
3. **Client** attaches to the sentinel and creates a **conversation** (task):

   * Calls `start_task(id=<conversation_id>, payload={"system_prompt": ...})`.
   * The agent stores a `ConversationState` (system prompt, history, `max_history_length`).
4. **Turns**: the client calls `run_turn(conversation_id, user_message)` repeatedly.

   * The agent builds the OpenAI **messages**: `[system] + recent history` (bounded window) and calls the LLM.
   * The agent appends the assistant reply to history and returns the text.
5. **End**: the client sends `end_conversation(conversation_id)` to clear state.

---

## Agent details

* `ConversationState` holds a `system_prompt`, `history`, and `max_history_length` (default **10**).
* On each turn, the agent trims history to keep the last `2 * max_history_length` messages (user+assistant pairs).
* LLM calls use `model = os.getenv("MODEL_NAME", "gpt-4.1-mini")` and require `OPENAI_API_KEY`.

---

## Environment variables

**Agent container**

```ini
FAME_DIRECT_ADMISSION_URL=ws://sentinel:8000/fame/v1/attach/ws/downstream
OPENAI_API_KEY=...            # required
MODEL_NAME=gpt-4.1-mini       # optional override
```

**Client (host)**

```ini
FAME_DIRECT_ADMISSION_URL=ws://localhost:8000/fame/v1/attach/ws/downstream
```

> The `run-verbose` target sets `FAME_SHOW_ENVELOPES=true` to print envelope metadata for learning/debugging.

---

## Run it

```bash
make start       # start the sentinel and chat agent
make run         # launch the interactive REPL client
make run-verbose # same as run, but prints envelope metadata
make stop        # tear down containers
```

When prompted, type your question at `Q> `. The agent replies as `A> ...`. Type `exit` to end the conversation.

---

## Troubleshooting

* **OpenAI auth error** — set `OPENAI_API_KEY` (and check org/project permissions if applicable).
* **Model not found** — set `MODEL_NAME` to a model available to your key.
* **Client can’t connect** — ensure the sentinel is healthy on port **8000** and the client’s `FAME_DIRECT_ADMISSION_URL` points to `ws://localhost:8000/...`.
* **No replies** — confirm the agent attached to the sentinel; try `make run-verbose` to see message traffic.

---

## Variations to try

* Change the **system prompt** (e.g., “You are a concise technical assistant”).
* Swap the **model** via `MODEL_NAME`.
* Extend `ChatAgent` to stream partial tokens back to the client.
