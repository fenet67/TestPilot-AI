import { useCallback, useEffect, useState } from 'react'
import './App.css'

/** Mirrors backend/app/schemas/health.py — keep them in sync by hand for now. */
type HealthResponse = {
  status: 'ok' | 'degraded'
  service: string
  version: string
  environment: string
}

type Connection =
  | { state: 'checking' }
  | { state: 'online'; health: HealthResponse }
  | { state: 'offline'; message: string }

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export default function App() {
  const [connection, setConnection] = useState<Connection>({ state: 'checking' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    setConnection({ state: 'checking' })

    async function probeBackend() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
          signal: controller.signal,
          headers: { Accept: 'application/json' },
        })
        if (!response.ok) {
          throw new Error(`Backend answered with HTTP ${response.status}`)
        }
        const health = (await response.json()) as HealthResponse
        setConnection({ state: 'online', health })
      } catch (error) {
        if (controller.signal.aborted) return
        setConnection({
          state: 'offline',
          message: error instanceof Error ? error.message : 'Unknown network error',
        })
      }
    }

    void probeBackend()
    return () => controller.abort()
  }, [attempt])

  const retry = useCallback(() => setAttempt((value) => value + 1), [])

  return (
    <main className="page">
      <header className="masthead">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-name">TestPilot AI</span>
        </div>
        <span className="badge">Day 1 · Foundation</span>
      </header>

      <section className="intro">
        <h1>An AI agent that tests web applications for you.</h1>
        <p className="lede">
          This is the Day 1 scaffold: a FastAPI backend, a typed React frontend, and a live health
          check between them. Browser automation arrives on Day 3, the agent on Day 12, and this
          screen is replaced by the real dashboard on Day 5.
        </p>
      </section>

      <section className="card" aria-live="polite">
        <div className="card-head">
          <h2>Backend connection</h2>
          <StatusDot state={connection.state} />
        </div>

        {connection.state === 'checking' && <p className="muted">Contacting the API…</p>}

        {connection.state === 'online' && (
          <div className="status-body">
            <p className="status-line ok">
              Connected to {connection.health.service} v{connection.health.version}
            </p>
            <dl className="facts">
              <div>
                <dt>Endpoint</dt>
                <dd>
                  <code>{API_BASE_URL}/api/v1/health</code>
                </dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{connection.health.status}</dd>
              </div>
              <div>
                <dt>Environment</dt>
                <dd>{connection.health.environment}</dd>
              </div>
            </dl>
          </div>
        )}

        {connection.state === 'offline' && (
          <div className="status-body">
            <p className="status-line down">Backend unreachable — {connection.message}</p>
            <p className="muted">
              Start it with <code>uvicorn app.main:app --reload --port 8000</code> from{' '}
              <code>backend/</code>, then try again.
            </p>
            <button type="button" className="button" onClick={retry}>
              Retry connection
            </button>
          </div>
        )}
      </section>

      <section className="stack">
        <h2>What exists today</h2>
        <ul className="checklist">
          <li>
            <strong>FastAPI service</strong> — app factory, versioned router, validated settings,
            CORS bound to the dev origin.
          </li>
          <li>
            <strong>Health endpoint</strong> — <code>GET /api/v1/health</code>, schema-validated and
            documented in Swagger.
          </li>
          <li>
            <strong>React + TypeScript</strong> — Vite dev server, strict types, typed API call with
            loading, error and success states.
          </li>
          <li>
            <strong>Tests</strong> — in-process API tests, run with <code>pytest</code>.
          </li>
        </ul>
        <p className="muted small">
          Files: <code>backend/app/main.py</code>, <code>backend/app/api/routes/health.py</code>,{' '}
          <code>frontend/src/App.tsx</code>, <code>docs/architecture.md</code>.
        </p>
      </section>
    </main>
  )
}

function StatusDot({ state }: { state: Connection['state'] }) {
  const label =
    state === 'online' ? 'Connected' : state === 'offline' ? 'Disconnected' : 'Checking'
  return (
    <span className={`pill pill-${state}`}>
      <span className="dot" aria-hidden="true" />
      {label}
    </span>
  )
}
