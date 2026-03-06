# Vape Calculator — Development TODO

Check off tasks as they are completed. Phases are sequential; complete each before moving on.

---

## Phase 1 — Project Scaffold & Core Calculator

### Setup
- [x] Create root project folder structure (`frontend/`, `backend/`, `docker/`, `docs/`, `data/`)
- [x] Create `.gitignore`
- [x] Create `.env.example`
- [x] Initialize git repository

### Backend
- [x] `cd backend && python -m venv .venv && source .venv/bin/activate`
- [x] Install: `fastapi uvicorn sqlmodel alembic pydantic pytest httpx`
- [x] Create `backend/app/main.py` with FastAPI app and `/health` endpoint
- [x] Create `backend/app/database.py` with SQLite connection
- [x] Create `backend/app/config.py` reading env vars
- [x] Create `backend/app/engine/calculator.py` — pure calculation logic
- [x] Create `backend/tests/test_calculator.py` — unit tests for all math scenarios
- [x] Run tests: `pytest backend/tests/test_calculator.py` — 17/17 passed
- [x] Create `backend/app/routes/calculator.py` — `POST /api/calculate` endpoint
- [x] Register calculator route in `main.py`

### Frontend
- [x] `npx sv create frontend` (SvelteKit, TypeScript, minimal template)
- [x] `cd frontend && npm install`
- [x] Install TailwindCSS: `npm install -D tailwindcss @tailwindcss/vite`
- [x] Configure `svelte.config.js` with `adapter-static`
- [x] Create `frontend/src/lib/api/client.ts` with `calculate()` API call
- [x] Create `frontend/src/lib/stores/recipe.ts` — writable store for active recipe
- [x] Build `Calculator.svelte` component:
  - [x] Recipe name input
  - [x] Batch size input (ml)
  - [x] Target nicotine strength input
  - [x] Nic base strength input
  - [x] Nic base PG/VG inputs
  - [x] PG/VG target ratio inputs (linked, sum = 100)
  - [x] Dynamic flavor rows with add/remove buttons
- [x] Build `ResultsPanel.svelte`:
  - [x] Ingredient table (name, ml, grams, %)
  - [x] Warning display
- [x] Wire store → debounced API call → results update (150ms debounce)
- [x] Basic layout in `+layout.svelte`

### Milestone check
- [x] Math matches manual calculation (17 unit tests pass)
- [x] All `test_calculator.py` tests pass
- [ ] Enter a 100ml, 3mg, 30/70, 15% TFA recipe → correct ml values displayed (verify in browser with backend running)

---

## Phase 2 — Recipe Save/Load

### Backend
- [x] Create DB models: `backend/app/models/recipe.py` (Recipe, RecipeFlavor)
- [x] Configure `alembic.ini` + `alembic/env.py` + `alembic/script.py.mako`
- [x] Create and apply initial migration (`initial_recipes`)
- [x] `POST /api/recipes` — create recipe + flavors
- [x] `GET /api/recipes` — list recipes (sortable by date/name)
- [x] `GET /api/recipes/{id}` — get full recipe with flavors
- [x] `PUT /api/recipes/{id}` — update recipe
- [x] `DELETE /api/recipes/{id}` — delete recipe (cascade flavors)
- [x] `POST /api/recipes/{id}/clone` — clone with parent_id set

### Frontend
- [x] "Save Recipe" button on calculator page (with success/error feedback)
- [x] Recipe list route `recipes/+page.svelte`:
  - [x] Search/filter by name
  - [x] Sort by date, name
  - [x] Delete with confirm dialog
  - [x] Clone button
- [x] Recipe detail route `recipes/[id]/+page.svelte`
- [x] "Load into Calculator" button on recipe detail
- [x] Populate all calculator fields from loaded recipe

### Milestone check
- [x] Save a recipe → appears in recipe list (verify in browser)
- [x] Reload app → recipe still there (verify in browser)
- [x] Clone recipe → new recipe with "(copy)" in name (verify in browser)
- [x] Delete recipe → removed from list (verify in browser)

---

## Phase 3 — Ingredient Database

### Backend
- [x] Create DB model: `backend/app/models/flavor.py`, `nic_base.py`
- [x] Apply migration for flavors and nic_bases tables
- [x] Create `backend/seeds/flavors.json` with ~100 common flavors (TFA, CAP, FA, FLV, INW, OOO, WF)
- [x] Create `backend/app/seed.py` (runs if flavors table is empty)
- [x] `GET /api/flavors?q=` — search endpoint (name + manufacturer filter)
- [x] `POST /api/flavors` — add custom flavor
- [x] `PUT /api/flavors/{id}` — update
- [x] `DELETE /api/flavors/{id}` — delete
- [x] Nic base CRUD: `GET/POST/PUT/DELETE /api/nic-bases`

### Frontend
- [x] `FlavorSearch.svelte` — typeahead component using Fuse.js
- [x] Replace plain flavor name input with FlavorSearch in FlavorRow
- [x] Auto-fill PG ratio / density on flavor select
- [x] Flavor management page `flavors/+page.svelte`:
  - [x] Browse all flavors
  - [x] Search/filter
  - [x] Add custom flavor form
  - [x] Edit/delete (admin actions)
- [x] Install Fuse.js: `npm install fuse.js`
- [x] Load flavors list at app startup into a store for instant search

### Milestone check
- [x] Type "TFA Str" → "TFA Strawberry" appears in dropdown
- [x] Select it → PG ratio auto-fills to 1.0
- [x] Custom flavor added and searchable immediately

---

## Phase 4 — Cost Calculator

### Backend
- [x] Add `pg_cost_per_ml` and `vg_cost_per_ml` to app settings (DB or config)
- [x] Ensure cost fields exist in flavor/nic_base models
- [x] Cost calculation already in engine — verify it works end to end

### Frontend
- [x] `CostPanel.svelte` — cost breakdown section in results:
  - [x] Cost per ingredient (inline)
  - [x] Total recipe cost
  - [x] Cost per ml
  - [x] Cost per bottle size (10ml, 30ml, 60ml, 100ml, 120ml)
- [x] Inline price input on each flavor row
- [x] PG/VG/Nic base price inputs (global settings)
- [x] Price settings persist to localStorage

### Milestone check
- [x] Set flavor prices → see cost breakdown update live
- [x] "Cost per 60ml bottle" is correct

---

## Phase 5 — Label Generator

### Backend
- [ ] Add to `requirements.txt`: `weasyprint>=60.0 jinja2>=3.1`
- [ ] Update Dockerfile with WeasyPrint system deps
- [ ] Create `backend/seeds/templates/default_label.html`
- [ ] Copy seed template to `/data/templates/` in `seed.py`
- [ ] Create DB model: `backend/app/models/label.py` (LabelTemplate)
- [ ] Apply migration for label_templates table
- [ ] `POST /api/labels/generate` — render template + return PDF stream
- [ ] `GET /api/labels/preview/{recipe_id}` — return rendered HTML
- [ ] `GET /api/labels/templates` — list available templates
- [ ] `POST /api/labels/templates/upload` — upload .html template file

### Frontend
- [ ] Label generator page `labels/+page.svelte`:
  - [ ] Recipe selector (load saved recipe)
  - [ ] Template picker dropdown
  - [ ] Label size selector
  - [ ] `LabelPreview.svelte` — iframe showing rendered HTML
  - [ ] "Download PDF" button
  - [ ] "Upload Template" file input

### Milestone check
- [ ] Select a recipe → label preview renders in iframe
- [ ] Click Download → get a properly sized PDF
- [ ] Upload custom template → appears in picker and renders

---

## Phase 6 — Recipe Rating & Notes

### Backend
- [x] Apply migration for recipe_ratings table
- [x] `POST /api/recipes/{id}/ratings` — add rating + note
- [x] `GET /api/recipes/{id}/ratings` — list ratings history
- [x] Update `GET /api/recipes` to support `sort=rating` query param

### Frontend
- [x] `StarRating.svelte` — clickable 1–5 star widget
- [x] Add rating widget to recipe detail page
- [x] Notes field with Markdown rendering (`marked` library)
- [x] Rating history list on recipe detail
- [x] Sort dropdown on recipe list page: date, name, rating
- [x] Filter by minimum rating

### Milestone check
- [x] Rate a recipe 5 stars → persists after reload
- [x] Sort recipe list by rating → highest rated first
- [x] Markdown notes render correctly

---

## Phase 7 — UI Polish

### Layout & Responsiveness
- [x] Mobile-responsive nav (hamburger drawer on small screens)
- [x] Stacked card layout on mobile
- [x] Fixed-width calculator layout on desktop

### Features
- [x] Dark mode toggle (CSS custom properties, localStorage)
- [x] Printable recipe card (`@media print` stylesheet)
- [x] Export recipe as JSON (download button)
- [x] Import recipe from JSON file
- [x] Keyboard shortcuts: Tab navigation, Ctrl+S to save
- [x] Error toast notification component
- [x] Loading spinners on async operations
- [x] Onboarding help text for first-time users

### Component Library
- [ ] Install `bits-ui` or `shadcn-svelte` for accessible primitives
- [x] Install `lucide-svelte` for icons
- [x] Install `marked` for Markdown

### Performance
- [x] Run `npm run build` and check bundle sizes
- [x] Verify route-level code splitting is working
- [ ] Test on mobile viewport (Chrome DevTools)

### Milestone check
- [ ] Looks good on 375px wide screen
- [ ] Dark mode works and persists
- [ ] Recipe card prints cleanly

---

## Phase 8 — Docker & Deployment

### Docker
- [x] Write multi-stage `docker/Dockerfile`:
  - [x] Stage 1: Node 20 → `npm run build` frontend
  - [x] Stage 2: Python 3.12-slim + WeasyPrint deps
  - [x] Copy frontend build into static/
  - [x] CMD: migrate → seed → uvicorn
- [x] Write `docker/docker-compose.yml` with volume and port config
- [x] Write `.env.example`
- [ ] Test full build: `docker compose build`
- [ ] Test full run: `docker compose up`
- [ ] Verify `/health` endpoint responds
- [ ] Verify frontend loads at `http://localhost:3000`
- [ ] Verify recipe save/load works with persistent volume
- [ ] Verify label PDF generation works inside container

### Unraid
- [ ] Deploy to Unraid server
- [ ] Verify data persists across container restarts
- [ ] (Optional) Create Unraid CA XML template

### Documentation
- [ ] Write `README.md` with setup instructions
- [ ] Document all environment variables in `.env.example`

### Milestone check
- [ ] `docker compose up -d` on Unraid → app accessible on local network
- [ ] Container restarts without data loss
- [ ] Full workflow: create recipe → save → rate → print label

---

## Post-MVP Backlog

- [ ] Inventory tracking (quantity on hand per ingredient)
- [ ] Shopping list generator
- [ ] Steep timer / batch log
- [ ] PWA manifest for mobile install
- [ ] Multi-user auth (JWT)
- [ ] Recipe JSON export/share via URL
- [ ] AI flavor pairing suggestions (Claude API)
- [ ] Flavor tasting notes database
- [ ] Price history tracking per ingredient
- [ ] Multiple labels per PDF page (A4 sheet)
