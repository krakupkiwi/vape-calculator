# Label Generation System

Bottle labels are generated as print-ready PDFs using a Jinja2 HTML template rendered by WeasyPrint.
No Chromium or headless browser is required.

---

## Pipeline

```
Recipe Data
    │
    ▼
POST /api/labels/generate
    │
    ▼
Jinja2 template (HTML/CSS)
    │
    ▼
WeasyPrint → PDF bytes
    │
    ▼
StreamingResponse → browser download
```

---

## Default Label Template

Stored at: `/data/templates/default_label.html`
Seeded into the container on first run.

```html
<!DOCTYPE html>
<html>
<head>
<style>
  @page {
    size: 100mm 50mm;
    margin: 3mm;
  }
  body {
    font-family: 'Liberation Sans', 'Arial', sans-serif;
    font-size: 8pt;
    width: 94mm;
    height: 44mm;
    overflow: hidden;
  }
  .header    { font-size: 12pt; font-weight: bold; text-align: center; }
  .subheader { text-align: center; font-size: 9pt; color: #444; margin-bottom: 2mm; }
  .specs     { display: flex; justify-content: space-around; margin: 2mm 0; }
  .spec-box  {
    text-align: center;
    border: 1px solid #999;
    padding: 1mm 3mm;
    border-radius: 2mm;
    font-size: 8pt;
  }
  .flavors   { font-size: 7pt; margin-top: 2mm; }
  .footer    { font-size: 6pt; color: #666; text-align: right; margin-top: 2mm; }
</style>
</head>
<body>
  <div class="header">{{ recipe_name }}</div>
  <div class="subheader">{{ author }}</div>

  <div class="specs">
    <div class="spec-box">
      <strong>{{ nic_strength }}mg</strong><br>Nicotine
    </div>
    <div class="spec-box">
      <strong>{{ pg_ratio }}/{{ vg_ratio }}</strong><br>PG/VG
    </div>
    <div class="spec-box">
      <strong>{{ batch_size }}ml</strong><br>Volume
    </div>
  </div>

  <div class="flavors">
    <strong>Flavors:</strong>
    {% for flavor in flavors %}
      {{ flavor.name }} ({{ flavor.percentage }}%){% if not loop.last %}, {% endif %}
    {% endfor %}
  </div>

  <div class="footer">Mixed: {{ date }} | {{ recipe_name }}</div>
</body>
</html>
```

### Template Variables

| Variable | Type | Example |
|---|---|---|
| `recipe_name` | string | "Strawberry Custard" |
| `author` | string | "Local User" |
| `nic_strength` | number | 3 |
| `pg_ratio` | number | 30 |
| `vg_ratio` | number | 70 |
| `batch_size` | number | 100 |
| `date` | string | "2026-03-05" |
| `flavors` | list | [{name, percentage}, ...] |

---

## Backend Endpoint

```python
# backend/app/routes/labels.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from typing import List
import io

router = APIRouter()
jinja_env = Environment(loader=FileSystemLoader("/data/templates"))

class LabelFlavor(BaseModel):
    name: str
    percentage: float

class LabelRequest(BaseModel):
    recipe_name: str
    author: str = "Local User"
    nic_strength: float
    pg_ratio: int
    vg_ratio: int
    batch_size: float
    date: str
    flavors: List[LabelFlavor]
    template_name: str = "default_label.html"

@router.post("/labels/generate")
def generate_label(payload: LabelRequest):
    template = jinja_env.get_template(payload.template_name)
    html_str = template.render(**payload.model_dump())
    pdf_bytes = HTML(string=html_str, base_url="/data/templates").write_pdf()
    filename = f"{payload.recipe_name.replace(' ', '_')}_label.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
```

---

## Custom Template Upload

Users can upload their own `.html` label templates:

- Uploaded to `/data/templates/`
- Registered in `label_templates` DB table
- Available in the template picker dropdown in the UI
- Same Jinja2 variable contract applies

### Upload endpoint

```
POST /api/labels/templates/upload
Content-Type: multipart/form-data
```

---

## UI Integration

1. User configures recipe in calculator
2. Clicks "Generate Label" button
3. Label preview renders in an `<iframe>` (GET endpoint returns HTML, not PDF)
4. "Download PDF" triggers the POST endpoint
5. Browser receives PDF for printing

### Preview endpoint (HTML only, no PDF)

```
GET /api/labels/preview/{recipe_id}?template=default_label.html
→ returns rendered HTML string directly
```

---

## Label Sizes

Common label sizes supported via `@page` CSS:

| Label | Size |
|---|---|
| Small bottle | 60mm × 40mm |
| Standard | 100mm × 50mm |
| Large | 120mm × 60mm |
| Full sheet (multiple) | A4 with grid layout |

Multiple labels per page can be implemented with a wrapper template that repeats the label block in a CSS grid.

---

## Dependencies

```
# requirements.txt additions
weasyprint>=60.0
jinja2>=3.1
```

WeasyPrint requires system libraries for fonts and Cairo. These are installed in the Dockerfile:

```dockerfile
RUN apt-get install -y \
    libpango-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev libcairo2 \
    fonts-liberation
```

> **Note:** WeasyPrint does NOT work natively on Windows. Develop and test label generation inside Docker.
