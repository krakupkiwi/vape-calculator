# Development Roadmap

---

## Phase 1 — Project Scaffold & Core Calculator
**Goal:** Working calculator with no persistence. Math verified.

### Tasks
- [ ] Initialize project structure (`frontend/`, `backend/`, `docker/`, `docs/`)
- [ ] Initialize SvelteKit project in `frontend/` with `adapter-static`
- [ ] Install TailwindCSS in frontend
- [ ] Initialize FastAPI project in `backend/`
- [ ] Set up SQLite with SQLModel and Alembic
- [ ] Implement `backend/app/engine/calculator.py` (pure functions, no DB)
- [ ] Write tests for calculator engine (`backend/tests/test_calculator.py`)
- [ ] Build `POST /api/calculate` endpoint (stateless)
- [ ] Build calculator UI:
  - Recipe name input
  - Batch size input
  - Nicotine strength input
  - Nic base strength input
  - PG/VG ratio slider or paired inputs
  - Dynamic flavor rows (add/remove)
  - Live recalculation on input change (debounced 150ms)
- [ ] Results panel:
  - ml per ingredient
  - grams per ingredient
  - Total ml verification

### Libraries
- `fastapi`, `uvicorn`, `sqlmodel`, `pydantic`, `alembic`
- `sveltekit`, `tailwindcss`

### Milestone
Enter a recipe → see exact ingredient volumes instantly. Math verified by tests.

---

## Phase 2 — Recipe Save/Load
**Goal:** Persist and retrieve recipes.

### Tasks
- [ ] Apply DB schema migration (recipes, recipe_flavors tables)
- [ ] `POST /api/recipes` — save recipe with flavors
- [ ] `GET /api/recipes` — list all recipes (name, date, nic, batch size)
- [ ] `GET /api/recipes/{id}` — load full recipe
- [ ] `PUT /api/recipes/{id}` — update recipe
- [ ] `DELETE /api/recipes/{id}` — delete with confirm dialog
- [ ] `POST /api/recipes/{id}/clone` — duplicate recipe (sets parent_id)
- [ ] Recipe list page: search by name, sort by date/name
- [ ] Load recipe into calculator (populate all fields)
- [ ] Recipe metadata: notes field (textarea), author

### Milestone
Save a recipe, reload it next session, clone it for variation testing.

---

## Phase 3 — Ingredient Database
**Goal:** Searchable flavor library with auto-fill.

### Tasks
- [ ] Apply DB migration (flavors, nic_bases tables)
- [ ] Seed DB with common flavor manufacturers: TFA, CAP, FA, FLV, INW, OOO, WF
- [ ] `GET /api/flavors?q=strawberry` — search endpoint
- [ ] `POST /api/flavors` — add custom flavor
- [ ] `PUT /api/flavors/{id}` — edit flavor (admin)
- [ ] `DELETE /api/flavors/{id}` — delete flavor (admin)
- [ ] Typeahead search in flavor row inputs
- [ ] Auto-fill PG/VG ratio and density when flavor is selected
- [ ] Nic base CRUD endpoints (`/api/nic-bases`)
- [ ] Flavor management page (admin view)
- [ ] "Add custom" flavor flow from calculator without leaving the page

### Libraries
- Fuse.js (fuzzy search, frontend-side for instant results)

### Milestone
Type "TFA Str" → see "TFA Strawberry" suggestion → select → PG ratio auto-fills.

---

## Phase 4 — Cost Calculator
**Goal:** Full cost breakdown per recipe, live.

### Tasks
- [ ] Add `cost_per_ml` to flavors, nic_bases (already in schema)
- [ ] Add `pg_cost_per_ml`, `vg_cost_per_ml` to app settings (stored in DB or env)
- [ ] Cost calculation in engine (already designed)
- [ ] Cost breakdown panel in results:
  - Cost per ingredient
  - Total recipe cost
  - Cost per ml
  - Cost per standard bottle sizes (10ml, 30ml, 60ml, 100ml, 120ml)
- [ ] Inline price editing on ingredient rows
- [ ] Price settings page (bulk edit ingredient prices)

### Milestone
See "$2.47 total / $0.082/ml / $4.92 per 60ml bottle" update live as you type.

---

## Phase 5 — Label Generator
**Goal:** Print-ready PDF bottle labels from recipe data.

### Tasks
- [ ] Install WeasyPrint and Jinja2 in backend
- [ ] Install system deps in Dockerfile
- [ ] Seed default label template to `/data/templates/`
- [ ] `POST /api/labels/generate` — returns PDF stream
- [ ] `GET /api/labels/preview/{recipe_id}` — returns HTML preview
- [ ] Label preview iframe panel in UI
- [ ] "Download Label" button triggers PDF download
- [ ] Template picker (select from available templates)
- [ ] `POST /api/labels/templates/upload` — upload custom .html template
- [ ] Template management page
- [ ] Label size selector (small/standard/large/sheet)

### Milestone
Click "Print Label" → download a 100mm×50mm PDF ready for printing.

---

## Phase 6 — Recipe Rating & Notes
**Goal:** Personal recipe quality tracking.

### Tasks
- [ ] Star rating widget (1–5) in recipe detail view
- [ ] `POST /api/ratings` endpoint
- [ ] `GET /api/recipes/{id}/ratings` — rating history
- [ ] Notes field with Markdown rendering (use `marked` or `marked-it`)
- [ ] Sort recipe list by: rating, date, name, batch size
- [ ] Filter by rating (show only 4+ star recipes)
- [ ] Recipe version history: store snapshot JSON on each save

### Milestone
Rate a recipe 5 stars, add a tasting note, sort recipe list by top-rated.

---

## Phase 7 — UI Polish
**Goal:** Production-quality UX, mobile-first.

### Tasks
- [ ] Mobile-responsive layout (drawer navigation, stacked cards)
- [ ] Dark mode toggle (CSS custom properties, persisted to localStorage)
- [ ] Printable recipe card (CSS `@media print`)
- [ ] Keyboard shortcuts:
  - Enter on flavor name → move to % field
  - Tab through fields naturally
  - Ctrl+S to save recipe
- [ ] Onboarding tooltips for new users (first-visit state)
- [ ] Import recipe from JSON file
- [ ] Export recipe as JSON
- [ ] Bundle size audit and lazy loading for route chunks
- [ ] Error toast notifications for API failures
- [ ] Loading states on all async operations

### Libraries
- `shadcn-svelte` or `bits-ui` for accessible components
- `lucide-svelte` for icons
- `marked` for Markdown rendering

### Milestone
App looks and feels professional on desktop and phone. Loads in under 1 second.

---

## Phase 8 — Docker & Deployment
**Goal:** One-command deploy on Unraid.

### Tasks
- [ ] Multi-stage Dockerfile (Node build → Python runtime)
- [ ] `docker-compose.yml` with volume, ports, env
- [ ] Health check endpoint `GET /health`
- [ ] DB migration runs automatically on container start
- [ ] Seed script runs only if DB is empty (idempotent)
- [ ] Default label template copied to `/data/templates/` on first run
- [ ] `.env.example` file with all configuration options
- [ ] Test full build and run cycle locally via Docker
- [ ] Unraid Community Apps XML template
- [ ] Deployment documentation in `docs/docker-deployment.md`

### Milestone
`docker compose up` on Unraid, app live and functional in under 60 seconds.

---

## Future Phases (Post-MVP)

| Feature | Notes |
|---|---|
| Inventory tracking | Track quantities on hand, warn when low |
| Shopping list | Generate buy list for planned batches |
| Steep timer | Track which batches are steeping |
| Batch log | Record every actual mix with date/notes |
| PWA support | Installable on mobile |
| Multi-user auth | JWT auth for shared household use |
| Recipe export/share | JSON export with import-by-URL |
| AI flavor pairing | Claude API integration for suggestions |
| Flavor notes DB | Community tasting notes per flavor |
