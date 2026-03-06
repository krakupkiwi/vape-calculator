from datetime import date
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.database import get_session
from app.models.recipe import Recipe

router = APIRouter()

DATA_TEMPLATES_DIR = Path("/data/templates")
ALLOWED_SIZE = 512 * 1024  # 512 KB max upload


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class LabelRequest(BaseModel):
    recipe_id: int
    template_name: str = Field(default="default_label.html")
    page_width: float = Field(default=62.0, gt=0, description="mm")
    page_height: float = Field(default=29.0, gt=0, description="mm")
    author: str = Field(default="")


class TemplateInfo(BaseModel):
    name: str
    size_bytes: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_context(recipe: Recipe, author: str, page_width: float, page_height: float) -> dict:
    pg_pct = round(recipe.pg_ratio * 100)
    vg_pct = round(recipe.vg_ratio * 100)
    flavors = [
        {"name": f.custom_name or "Unknown", "percentage": f.percentage}
        for f in sorted(recipe.flavors, key=lambda x: x.sort_order)
    ]
    return {
        "recipe_name": recipe.name,
        "author": author or "Unknown",
        "nic_strength": round(recipe.target_nic_mg, 1),
        "pg_ratio": pg_pct,
        "vg_ratio": vg_pct,
        "batch_size": round(recipe.batch_size_ml, 1),
        "flavors": flavors,
        "date": date.today().strftime("%Y-%m-%d"),
        "page_width": page_width,
        "page_height": page_height,
    }


def _render_template(template_name: str, context: dict) -> str:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(
        loader=FileSystemLoader(str(DATA_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template(template_name)
    return template.render(**context)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/labels/templates", response_model=List[TemplateInfo])
def list_templates() -> List[TemplateInfo]:
    """List all available label templates in /data/templates/."""
    DATA_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    templates = []
    for p in sorted(DATA_TEMPLATES_DIR.glob("*.html")):
        templates.append(TemplateInfo(name=p.name, size_bytes=p.stat().st_size))
    return templates


@router.post("/labels/preview", response_class=HTMLResponse)
def preview_label(
    payload: LabelRequest,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    """Render label as HTML (for iframe preview). Does NOT use WeasyPrint."""
    recipe = session.get(Recipe, payload.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    template_path = DATA_TEMPLATES_DIR / payload.template_name
    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{payload.template_name}' not found")

    context = _build_context(recipe, payload.author, payload.page_width, payload.page_height)
    html = _render_template(payload.template_name, context)
    return HTMLResponse(content=html)


@router.post("/labels/generate")
def generate_label_pdf(
    payload: LabelRequest,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Render label as PDF via WeasyPrint. Must be run inside Docker (Linux)."""
    try:
        from weasyprint import HTML as WeasyHTML
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="WeasyPrint is not available. Run inside Docker to generate PDFs.",
        )

    recipe = session.get(Recipe, payload.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    template_path = DATA_TEMPLATES_DIR / payload.template_name
    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{payload.template_name}' not found")

    context = _build_context(recipe, payload.author, payload.page_width, payload.page_height)
    html_str = _render_template(payload.template_name, context)

    pdf_bytes = WeasyHTML(string=html_str, base_url=str(DATA_TEMPLATES_DIR)).write_pdf()

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in recipe.name)
    filename = f"label_{safe_name}.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/labels/templates/upload", response_model=TemplateInfo, status_code=201)
async def upload_template(file: UploadFile = File(...)) -> TemplateInfo:
    """Upload a custom Jinja2 HTML label template."""
    if not file.filename or not file.filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="Only .html files are accepted.")

    contents = await file.read()
    if len(contents) > ALLOWED_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 512 KB).")

    DATA_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_TEMPLATES_DIR / Path(file.filename).name
    dest.write_bytes(contents)

    return TemplateInfo(name=dest.name, size_bytes=dest.stat().st_size)
