# Project Folder Structure

```
vape-calculator/
│
├── frontend/                          # SvelteKit application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── Calculator.svelte      # Main calculator form
│   │   │   │   ├── FlavorRow.svelte       # Individual flavor input row
│   │   │   │   ├── ResultsPanel.svelte    # Ingredient results table
│   │   │   │   ├── RecipeList.svelte      # Recipe browser/search
│   │   │   │   ├── RecipeCard.svelte      # Recipe summary card
│   │   │   │   ├── LabelPreview.svelte    # Label iframe preview
│   │   │   │   ├── StarRating.svelte      # 1–5 star rating widget
│   │   │   │   ├── CostPanel.svelte       # Cost breakdown display
│   │   │   │   └── FlavorSearch.svelte    # Typeahead flavor picker
│   │   │   ├── stores/
│   │   │   │   ├── recipe.ts              # Active recipe state
│   │   │   │   └── calculator.ts          # Calculation result state
│   │   │   ├── api/
│   │   │   │   └── client.ts              # Typed API wrapper functions
│   │   │   └── utils/
│   │   │       └── format.ts              # Number formatting helpers
│   │   ├── routes/
│   │   │   ├── +layout.svelte             # App shell, nav, dark mode
│   │   │   ├── +page.svelte               # Calculator home
│   │   │   ├── recipes/
│   │   │   │   ├── +page.svelte           # Recipe list
│   │   │   │   └── [id]/
│   │   │   │       └── +page.svelte       # Recipe detail / editor
│   │   │   ├── flavors/
│   │   │   │   └── +page.svelte           # Flavor DB browser
│   │   │   ├── labels/
│   │   │   │   └── +page.svelte           # Label generator UI
│   │   │   └── admin/
│   │   │       └── +page.svelte           # Admin: flavor/nic base CRUD
│   │   └── app.html                       # HTML shell
│   ├── static/                            # Static assets (favicon, fonts)
│   ├── package.json
│   ├── svelte.config.js                   # adapter-static config
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── backend/                           # FastAPI application
│   ├── app/
│   │   ├── main.py                    # FastAPI app, router mounts, static serve
│   │   ├── database.py                # SQLite engine, session factory
│   │   ├── config.py                  # Settings from environment variables
│   │   ├── seed.py                    # First-run seed script (idempotent)
│   │   ├── models/
│   │   │   ├── recipe.py              # Recipe, RecipeFlavor SQLModel classes
│   │   │   ├── flavor.py              # Flavor SQLModel class
│   │   │   ├── nic_base.py            # NicBase SQLModel class
│   │   │   └── label.py              # LabelTemplate SQLModel class
│   │   ├── routes/
│   │   │   ├── calculator.py          # POST /api/calculate
│   │   │   ├── recipes.py             # CRUD + clone + history
│   │   │   ├── flavors.py             # Flavor CRUD + search
│   │   │   ├── nic_bases.py           # Nic base CRUD
│   │   │   ├── ratings.py             # Recipe ratings
│   │   │   └── labels.py              # Label generate + template upload
│   │   └── engine/
│   │       └── calculator.py          # Pure calculation logic (no DB)
│   ├── seeds/
│   │   ├── flavors.json               # Seeded flavor list (TFA, CAP, FA, etc.)
│   │   ├── nic_bases.json             # Common nic base configs
│   │   └── templates/
│   │       └── default_label.html     # Default label template
│   ├── tests/
│   │   ├── test_calculator.py         # Unit tests for engine
│   │   └── test_api.py                # Integration tests for routes
│   ├── alembic/                       # DB migration scripts
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   └── requirements.txt
│
├── docker/
│   ├── Dockerfile                     # Multi-stage build
│   └── docker-compose.yml
│
├── data/                              # gitignored — mounted as Docker volume
│   ├── vape.db
│   ├── templates/
│   └── uploads/
│
├── docs/                              # This directory
│   ├── architecture.md
│   ├── database-schema.md
│   ├── calculation-engine.md
│   ├── label-generation.md
│   ├── docker-deployment.md
│   ├── roadmap.md
│   └── folder-structure.md
│
├── .env.example                       # Environment variable template
├── .gitignore
├── TODO.md                            # Development checklist
└── README.md
```

---

## Key File Purposes

| File | Purpose |
|---|---|
| `backend/app/engine/calculator.py` | The math. Pure functions. No side effects. Test this first. |
| `backend/app/main.py` | FastAPI entry point. Mounts routes then static files. |
| `backend/app/database.py` | SQLite connection string from env. Session dependency for routes. |
| `backend/app/seed.py` | Runs once on startup if DB is empty. Loads flavors.json. |
| `backend/seeds/flavors.json` | Curated list of ~200 common flavor concentrates with manufacturer and PG ratio. |
| `frontend/src/lib/api/client.ts` | All fetch() calls in one place. Typed request/response. |
| `frontend/src/lib/stores/recipe.ts` | Svelte writable store — single source of truth for the active recipe state. |
| `docker/Dockerfile` | Multi-stage: Node (build frontend) → Python (run everything). |
| `.env.example` | Documents all environment variables with safe defaults. |

---

## .gitignore Entries

```
data/
frontend/node_modules/
frontend/build/
frontend/.svelte-kit/
backend/__pycache__/
backend/.venv/
backend/*.egg-info/
.env
*.db
```
