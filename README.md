# TestPilot AI

> An AI agent that explores, tests, and evaluates web applications autonomously.

TestPilot AI is a software-testing platform that combines an LLM agent, browser automation and
evidence-based reporting. You give it a URL and a testing objective; it inspects the site, plans a
test strategy, generates structured test cases, executes them with Playwright, evaluates the
observable evidence, and produces bug reports backed by screenshots, console errors and network
failures.

**Status:** Day 1 of a 21-day build — foundation only. Nothing below is claimed to work until it
is implemented, tested and recorded in the daily report.

---

## Stack

| Layer | Technology | Introduced |
| --- | --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind + shadcn/ui (Day 5), Recharts (Day 17) | Day 1 |
| Backend | Python 3.13, FastAPI, Pydantic v2, pydantic-settings | Day 1 |
| Browser automation | Playwright (Chromium) | Day 3 |
| Database | PostgreSQL + SQLAlchemy + Alembic | Day 6 |
| AI | OpenAI Responses API, function calling, Structured Outputs | Day 8–12 |
| Jobs | Redis + Celery | Day 20 (if needed) |
| Deployment | Docker Compose | Day 20 |

Dependencies are added on the day they are needed, not up front.

---

## Repository layout

```
TestPilot-AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # app factory: middleware, routers, lifespan
│   │   ├── api/
│   │   │   ├── router.py        # aggregates versioned routers
│   │   │   └── routes/
│   │   │       └── health.py    # GET /api/v1/health
│   │   ├── core/
│   │   │   └── config.py        # validated settings from env
│   │   └── schemas/
│   │       └── health.py        # API contract for health
│   ├── tests/
│   │   └── test_health.py
│   ├── requirements.txt         # runtime deps
│   ├── requirements-dev.txt     # test/lint deps
│   ├── pyproject.toml           # pytest + ruff config
│   └── .env.example
├── frontend/                    # React + TypeScript (Vite)
├── docs/
│   └── architecture.md
├── logs/  artifacts/            # git-ignored runtime output
└── README.md
```

As the project grows, `backend/app/` gains `services/` (AI planners, evaluators), `agent/`
(the execution loop), `browser/` (Playwright tools), `db/` (models, sessions) and `workers/`.

---

## Getting started

Requirements: Python 3.13+, Node 20+, Git.

### Backend

```bash
cd backend
python -m venv .venv
cp .env.example .env            # PowerShell: Copy-Item .env.example .env
.venv/Scripts/python -m pip install -r requirements-dev.txt   # macOS/Linux: .venv/bin/python
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000/api/v1/health
- Swagger UI: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
cp .env.example .env.local      # PowerShell: Copy-Item .env.example .env.local
npm install
npm run dev                     # http://127.0.0.1:5173
```

### Tests and lint

```bash
cd backend
.venv/Scripts/python -m pytest
.venv/Scripts/python -m ruff check .
```

---

## Configuration and secrets

- Settings live in `backend/.env` (git-ignored); the shape is documented in `backend/.env.example`.
- The browser only receives `VITE_*` variables. **Never put a secret in a `VITE_*` variable** — those
  are compiled into the public bundle.
- LLM and database credentials are read server-side only, and are never returned by an API response
  or written to a log.

---

## Security posture

TestPilot AI will only test sites the operator owns or is authorised to test. The planned controls
(tracked in `docs/architecture.md`): URL allow-list, SSRF protection with private/internal IP
blocking and redirect re-validation, per-session timeouts and action caps, tool-argument validation,
browser isolation, and no arbitrary shell or Python execution by the model.

---

## Roadmap

| Week | Focus |
| --- | --- |
| 1 | Foundation: FastAPI + React, browser automation, PostgreSQL persistence |
| 2 | AI: LLM integration, Structured Outputs, planner, function calling, agent loop, execution |
| 3 | Intelligence: failure analysis, bug reports, dashboard, RAG, evaluation, Docker, deploy |

Daily progress reports are recorded in the chat as the project proceeds.
