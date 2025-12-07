# Multi-Agent Text Analysis Workflow (Python Backend + React Frontend)

This example demonstrates a **distributed multi-agent workflow** where:
- **Frontend**: React app running in the browser (using `@naylence/react`)
- **Backend**: Python agents running in Docker containers (using `naylence` Python SDK)

The client connects to the backend via WebSocket. The workflow agent orchestrates three worker agents (stats, keywords, sentences) and returns aggregated results.

---

## Architecture

```
Browser (React) ──WebSocket──▶ Sentinel (Python) ──▶ Workflow Agent (Python) 
                                                        ├─▶ Stats Agent
                                                        ├─▶ Keywords Agent
                                                        └─▶ Sentences Agent
```

---

## Components

### Backend (Python)

- **sentinel.py** — Runs the sentinel (fabric router at `:8000`)
- **workflow_agent.py** — Orchestrator that fans out to worker agents using `Agent.broadcast`
- **stats_agent.py** — Calculates text statistics (char count, word count, sentences, reading time)
- **keywords_agent.py** — Extracts top keywords (with stop word filtering)
- **sentences_agent.py** — Extracts sentence previews
- **common.py** — Shared agent addresses

### Frontend (React)

- **browser/src/App.tsx** — Main React app with envelope inspector
- **browser/src/ClientNode.tsx** — Browser client that connects via WebSocket
- **browser/src/EnvelopeInspector.tsx** — Debug UI for viewing message envelopes
- **browser/src/config.ts** — WebSocket connection configuration

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Make

### 1. Start the Backend

```bash
make start
```

This will:
1. Build Docker images
2. Start all Python agents (sentinel + 4 worker agents)
3. Expose sentinel on `http://localhost:8000`

### 2. Start the Frontend

In a separate terminal:

```bash
make run-frontend
```

This will:
1. Install npm dependencies
2. Start Vite dev server at `http://localhost:5173`

### 3. Use the App

1. Open browser to `http://localhost:5173`
2. Enter some text in the textarea
3. Click "Run Workflow"
4. View the analysis results (stats, keywords, sentences)
5. Click "Enable Debug" to see message envelopes

---

## Development

### View Logs

```bash
make logs
```

### Stop Backend

```bash
make stop
```

### Clean Everything

```bash
make clean
```

---

## How It Works

1. **Browser client** connects to sentinel via WebSocket (`ws://localhost:8000/fame/v1/attach/ws/downstream`)
2. User enters text and clicks "Run Workflow"
3. Client sends message to `workflow@fame.fabric` with `{ text: "..." }`
4. **Workflow agent** uses `Agent.broadcast()` to fan out to three worker agents in parallel
5. Each worker agent processes the text and returns results
6. Workflow agent aggregates results and returns to client
7. Client displays the combined analysis

---

## Key Differences from TypeScript Version

- Backend uses Python (`naylence` package) instead of TypeScript (`@naylence/agent-sdk`)
- Frontend is identical (React with `@naylence/react`)
- Docker image: `naylence/agent-sdk-python:0.3.14` instead of `naylence/agent-sdk-node:0.3.5`
- Python async/await syntax (`asyncio.run()`, `async def`)
- Type hints using Python `dict`, `list`, etc.

---

## Learn More

- [Naylence Python SDK Documentation](https://github.com/naylence)
- [Naylence React Documentation](https://github.com/naylence)
- [WebSocket Admission Guide](https://github.com/naylence)
