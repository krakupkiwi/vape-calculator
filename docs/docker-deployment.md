# Docker Deployment Plan

Target: Unraid server, single container, persistent SQLite volume.

---

## Container Architecture

```
Unraid Host
├── Port 3000 (configurable) ──▶ Container port 8000
└── /mnt/user/appdata/vapecalc/       ← persistent volume
    ├── vape.db                        ← SQLite database
    ├── templates/                     ← label HTML templates
    └── uploads/                       ← user uploads
```

Single container runs:
- FastAPI (uvicorn) on port 8000
- Serves SvelteKit static build from `/static`
- No nginx, no separate frontend container

---

## Dockerfile

```dockerfile
# docker/Dockerfile

# ── Stage 1: Build SvelteKit ──────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python runtime ───────────────────────────────────
FROM python:3.12-slim

# WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .

# Copy SvelteKit static build from stage 1
COPY --from=frontend-builder /build/build ./static

# Data directory (will be mounted as volume)
RUN mkdir -p /data/templates /data/uploads

# Copy seed data
COPY backend/seeds/ ./seeds/

EXPOSE 8000

# Run migrations then start server
CMD alembic upgrade head && \
    python -m app.seed && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## docker-compose.yml

```yaml
# docker/docker-compose.yml
version: "3.9"

services:
  vapecalc:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: vape-calculator
    restart: unless-stopped
    ports:
      - "${APP_PORT:-3000}:8000"
    volumes:
      - ${DATA_PATH:-./data}:/data
    environment:
      - DATABASE_URL=sqlite:////data/vape.db
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
      - APP_ENV=${APP_ENV:-production}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Environment Variables

Create `.env` next to `docker-compose.yml`:

```bash
# .env
APP_PORT=3000
DATA_PATH=/mnt/user/appdata/vapecalc
SECRET_KEY=replace-with-a-long-random-string
APP_ENV=production
```

---

## FastAPI Static File Mount

```python
# backend/app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Mount API routes first
app.include_router(calculator_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")
# ... other routers

# Serve SvelteKit static build — must come LAST
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
```

---

## Unraid Setup Steps

1. SSH into Unraid or open Terminal
2. Create the data directory:
   ```bash
   mkdir -p /mnt/user/appdata/vapecalc/templates
   ```
3. Copy `docker-compose.yml` and `.env` to `/mnt/user/appdata/vapecalc/`
4. Start the container:
   ```bash
   cd /mnt/user/appdata/vapecalc
   docker compose up -d
   ```
5. Access the app at `http://<unraid-ip>:3000`

### Updating

```bash
docker compose pull     # if using published image
docker compose up -d --build   # if building locally
```

---

## Unraid Community Applications Template (optional)

For one-click install via CA, create an XML template:

```xml
<?xml version="1.0"?>
<Container version="2">
  <Name>vape-calculator</Name>
  <Repository>ghcr.io/youruser/vape-calculator:latest</Repository>
  <Network>bridge</Network>
  <Privileged>false</Privileged>
  <Support/>
  <Overview>Self-hosted e-liquid recipe calculator</Overview>
  <Category>Tools:</Category>
  <WebUI>http://[IP]:[PORT:3000]/</WebUI>
  <ExtraParams>--restart=unless-stopped</ExtraParams>
  <Config Name="Web Port" Target="8000" Default="3000" Mode="tcp" Type="Port"/>
  <Config Name="Data Path" Target="/data" Default="/mnt/user/appdata/vapecalc" Mode="rw" Type="Path"/>
  <Config Name="Secret Key" Target="SECRET_KEY" Default="" Type="Variable"/>
</Container>
```

---

## Persistent Volume Contents

| Path in container | Contents | Backed up? |
|---|---|---|
| `/data/vape.db` | All recipes, flavors, ratings | YES — back this up |
| `/data/templates/` | Label HTML templates | YES |
| `/data/uploads/` | User-uploaded template files | YES |

The `static/` directory and Python code live inside the image — no persistence needed there.

---

## Health Check

```python
# backend/app/main.py

@app.get("/health")
def health():
    return {"status": "ok"}
```

Used by Docker's healthcheck and can be polled by Unraid for container status.
