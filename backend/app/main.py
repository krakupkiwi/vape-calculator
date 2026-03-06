from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

from app.routes import calculator as calculator_router
from app.routes import recipes as recipes_router
from app.routes import flavors as flavors_router
from app.routes import nic_bases as nic_bases_router
from app.routes import labels as labels_router

app = FastAPI(title="Vape Calculator API")


@app.on_event("startup")
def on_startup():
    cfg = AlembicConfig(str(Path(__file__).parent.parent / "alembic.ini"))
    alembic_command.upgrade(cfg, "head")
    from app.seed import run_seed, seed_templates
    run_seed()
    try:
        seed_templates()
    except Exception as e:
        print(f"[seed] WARNING: Could not copy label templates: {e}")


# --- API routes (must be registered BEFORE static files) ---
app.include_router(calculator_router.router, prefix="/api")
app.include_router(recipes_router.router, prefix="/api")
app.include_router(flavors_router.router, prefix="/api")
app.include_router(nic_bases_router.router, prefix="/api")
app.include_router(labels_router.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Serve SvelteKit static build (LAST) ---
STATIC_DIR = Path(__file__).parent.parent.parent / "frontend" / "build"

if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
