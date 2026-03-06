# System Architecture

## Philosophy

Monolith-first. Single deployable Docker container with clear internal separation. No microservices.

## Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | SvelteKit | Fast, lightweight, excellent reactive primitives |
| Backend API | FastAPI (Python) | Clean REST, typed, great PDF/math library ecosystem |
| Database | SQLite + SQLModel | Zero-server, file-based, perfect for single-user self-hosted |
| PDF Engine | WeasyPrint | Pure Python, no Chromium dependency |
| Container | Docker + Compose | Unraid-native deployment |

## Container Diagram

```
Unraid Host
│
├── Port 3000 ──▶ Container:8000
│
└── /mnt/user/appdata/vapecalc/
    ├── vape.db           (SQLite database)
    ├── templates/        (label HTML templates)
    └── uploads/          (user uploads)

┌─────────────────────────────────────────────────┐
│                  Docker Container                │
│                                                 │
│  ┌─────────────┐      ┌──────────────────────┐  │
│  │   SvelteKit  │─────▶│   FastAPI (Python)   │  │
│  │  (Frontend) │      │    (API + Engine)    │  │
│  └─────────────┘      └──────────┬───────────┘  │
│                                  │               │
│                        ┌─────────▼──────────┐   │
│                        │   SQLite Database  │   │
│                        │  /data/vape.db     │   │
│                        └────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │         Persistent Volume: /data        │    │
│  │   - vape.db  - uploads/  - templates/  │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

## How SvelteKit + FastAPI Are Served Together

- SvelteKit is built as a static site (`adapter-static`)
- The `build/` output is copied into the Docker image
- FastAPI serves static files from `/static` at route `/`
- Single process, single port — no nginx needed

## API Overview

```
GET    /health
POST   /api/calculate

GET    /api/recipes
POST   /api/recipes
GET    /api/recipes/{id}
PUT    /api/recipes/{id}
DELETE /api/recipes/{id}
POST   /api/recipes/{id}/clone
GET    /api/recipes/{id}/history

GET    /api/flavors
POST   /api/flavors
PUT    /api/flavors/{id}
DELETE /api/flavors/{id}

GET    /api/nic-bases
POST   /api/nic-bases

POST   /api/ratings

GET    /api/labels/templates
POST   /api/labels/generate
POST   /api/labels/templates/upload
```

## Data Flow: Live Calculation

```
User types in UI
      │
      ▼
Svelte store updated
      │
      ▼
$effect fires (debounced 150ms)
      │
      ▼
POST /api/calculate  (stateless, no DB write)
      │
      ▼
calculator.py engine
      │
      ▼
RecipeResult returned as JSON
      │
      ▼
Results panel re-renders reactively
```

## Key Design Decisions

- **Stateless `/calculate` endpoint** — the engine is pure functions, no DB dependency. Fast, testable.
- **SQLModel** merges Pydantic + SQLAlchemy — one model class serves both API validation and ORM.
- **WeasyPrint** chosen over Puppeteer to avoid bundling Chromium in the Docker image.
- **SQLite** is sufficient for a single-user self-hosted app; can be swapped for Postgres with minimal changes to `database.py`.
