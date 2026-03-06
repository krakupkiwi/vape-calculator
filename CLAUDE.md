# Vape Calculator — Claude Code Instructions

## Project Overview
Self-hosted e-liquid recipe calculator web app. Single Docker container deployed on Unraid.

Working directory: `s:\Vape Calculator Site`

## Tech Stack
- **Frontend:** SvelteKit with `adapter-static`, TailwindCSS, TypeScript
- **Backend:** FastAPI (Python 3.12), uvicorn
- **Database:** SQLite via SQLModel + Alembic migrations
- **PDF Labels:** WeasyPrint + Jinja2 (no Puppeteer, no Chromium)
- **Search:** Fuse.js (client-side fuzzy search)
- **Icons:** lucide-svelte
- **Components:** bits-ui or shadcn-svelte

## Project Structure
```
frontend/          SvelteKit app (adapter-static)
backend/           FastAPI app
  app/
    engine/        Pure calculation logic (no DB deps)
    models/        SQLModel ORM models
    routes/        FastAPI route handlers
    seeds/         Seed data (flavors.json, templates/)
  tests/           pytest tests
  alembic/         DB migrations
docker/            Dockerfile + docker-compose.yml
docs/              Architecture and reference docs
data/              Gitignored — Docker volume mount target
TODO.md            Development checklist (check off as you go)
```

## Key Reference Docs
- `docs/architecture.md` — system design and data flow
- `docs/database-schema.md` — full SQL schema
- `docs/calculation-engine.md` — math + complete Python implementation
- `docs/label-generation.md` — WeasyPrint pipeline
- `docs/docker-deployment.md` — Dockerfile, compose, Unraid setup
- `docs/roadmap.md` — 8 development phases
- `docs/folder-structure.md` — annotated file tree
- `TODO.md` — granular checkbox checklist for all phases

## Development Commands

### Backend
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest tests/
alembic upgrade head
```

### Frontend
```bash
cd frontend
npm install
npm run dev        # dev server at localhost:5173
npm run build      # outputs to frontend/build/
npm run check      # TypeScript check
```

### Docker
```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
```

## Architecture Rules

1. **FastAPI serves both API and static files.** No nginx. No separate frontend container.
2. **Static files mount LAST** in `main.py` — after all API routers are registered.
3. **`/api/calculate` is stateless** — no DB reads/writes. Pure engine call only.
4. **SQLModel** is used for all DB models. Do not use raw SQLAlchemy.
5. **Alembic** manages all schema changes. Never modify DB tables manually.
6. **Seed script is idempotent** — only inserts if the flavors table is empty.
7. **WeasyPrint does not work on Windows natively.** Test label generation inside Docker only.

## Calculation Engine Rules
- `backend/app/engine/calculator.py` must have zero framework dependencies (no FastAPI, no SQLModel)
- All calculation functions must be unit-testable in isolation
- Always write tests in `backend/tests/test_calculator.py` before wiring to API
- Negative V_pg or V_vg values → clamp to 0 and add a warning string, never raise an exception

## API Conventions
- All API routes are prefixed `/api/`
- Use Pydantic v2 models for request/response schemas
- Return HTTP 404 with `{"detail": "..."}` for missing resources
- Return HTTP 422 automatically via FastAPI for validation errors
- Calculation endpoint returns warnings array (never raises for impossible ratios)

## Frontend Conventions
- All API calls go through `frontend/src/lib/api/client.ts`
- Active recipe state lives in `frontend/src/lib/stores/recipe.ts`
- Calculator re-runs on any input change — debounced 150ms
- Use `$effect` (Svelte 5) or `$: {}` reactive blocks for live recalculation
- No hardcoded API URLs — use relative paths (FastAPI serves the frontend)

## Database
- SQLite file at `/data/vape.db` inside the container (mounted volume)
- Migrations live in `backend/alembic/versions/`
- Run `alembic revision --autogenerate -m "description"` to create a new migration
- Run `alembic upgrade head` to apply

## Docker / Unraid
- Persistent volume: `/data` inside container → `/mnt/user/appdata/vapecalc/` on host
- Port: container 8000 → host 3000 (configurable via APP_PORT env var)
- Container start order: migrate → seed → uvicorn
- Health check: `GET /health` returns `{"status": "ok"}`

## Development Order
Follow `TODO.md` phase by phase:
1. Calculator engine + tests (no UI yet)
2. FastAPI endpoint for calculate
3. SvelteKit calculator UI
4. Recipe save/load (CRUD)
5. Flavor DB + typeahead
6. Cost calculator
7. Label generator (Docker only for WeasyPrint)
8. Ratings + notes
9. UI polish
10. Docker deploy

## Do Not
- Do not use Puppeteer or any Chromium-based PDF tool
- Do not add microservices or separate containers
- Do not use nginx
- Do not use Postgres (SQLite only)
- Do not use React or Vue (SvelteKit only)
- Do not skip writing engine tests before building the API
