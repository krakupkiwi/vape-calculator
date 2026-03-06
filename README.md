# Vape Calculator

A self-hosted e-liquid recipe calculator. Calculate ingredient volumes, track costs, save recipes, rate batches, and print bottle labels — all in one Docker container.

![SvelteKit](https://img.shields.io/badge/SvelteKit-FF3E00?style=flat&logo=svelte&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Features

- **Calculator** — live ingredient breakdown (ml, grams, %) with PG/VG/nicotine math
- **Cost tracking** — per-ingredient and per-bottle cost breakdown
- **Recipe library** — save, load, clone, search, and sort recipes
- **Ratings & notes** — 1–5 star ratings with Markdown notes and history
- **Flavor database** — 100+ pre-loaded flavors (TFA, CAP, FA, FLV, INW, WF) with typeahead search
- **Label generator** — Jinja2 HTML templates rendered to PDF via WeasyPrint
- **Dark mode** — system-aware with manual toggle
- **Import/Export** — recipes as JSON

## Quick Start (Docker Compose)

```yaml
services:
  app:
    image: ghcr.io/krakupkiwi/vape-calculator:latest
    container_name: vapecalc
    ports:
      - "8484:8000"
    volumes:
      - /mnt/user/appdata/vapecalc:/data
    restart: unless-stopped
```

Or clone and build locally:

```bash
git clone https://github.com/krakupkiwi/vape-calculator.git
cd vape-calculator
docker compose -f docker/docker-compose.yml up -d --build
```

The app will be available at `http://localhost:8484`.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_PORT` | `8484` | Host port to expose the app on |
| `DATABASE_URL` | `sqlite:////data/vape.db` | SQLite database path |
| `APP_ENV` | `production` | Environment (`production` / `development`) |

Set these in a `.env` file next to your `docker-compose.yml`.

## Persistent Data

All data is stored in the `/data` volume mount:

| Path | Contents |
|---|---|
| `/data/vape.db` | SQLite database (recipes, flavors, ratings) |
| `/data/templates/` | Label HTML templates |

Map `/data` to a persistent location on your host (e.g. `/mnt/user/appdata/vapecalc` on Unraid).

## Updating

```bash
cd /path/to/vape-calculator
git pull
docker compose -f docker/docker-compose.yml up -d --build
```

Migrations run automatically on startup — no manual DB steps needed.

## Label Templates

Labels are Jinja2 HTML files rendered to PDF by WeasyPrint. The default template is sized for a 62×29mm Brother DK label roll.

**Available template variables:**

| Variable | Example |
|---|---|
| `{{ recipe_name }}` | Strawberry Custard |
| `{{ author }}` | Sam |
| `{{ nic_strength }}` | 3 |
| `{{ pg_ratio }}` / `{{ vg_ratio }}` | 30 / 70 |
| `{{ batch_size }}` | 100 |
| `{{ date }}` | 2026-03-06 |
| `{{ flavors }}` | list of `{name, percentage}` |
| `{{ page_width }}` / `{{ page_height }}` | 62 / 29 (mm) |

Custom templates can be uploaded via the Labels page. Embed images as base64 data URIs — WeasyPrint cannot load external URLs.

> **Note:** PDF generation requires WeasyPrint and only works inside the Docker container (Linux). The HTML preview always works, including on Windows.

## Local Development

**Backend**
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

**Run tests**
```bash
cd backend
pytest tests/
```

## Tech Stack

- **Frontend:** SvelteKit (adapter-static), TailwindCSS v4, TypeScript, Fuse.js, lucide-svelte
- **Backend:** FastAPI, uvicorn, SQLModel, Alembic, WeasyPrint, Jinja2
- **Database:** SQLite
- **Container:** Docker (multi-stage build — Node 20 → Python 3.12-slim)

## Unraid

1. Install the **Community Applications** plugin
2. Add a new container manually or use Docker Compose via the **ComposePal** plugin
3. Map port `8484` and set the data path to `/mnt/user/appdata/vapecalc`
4. Data survives container restarts and updates
