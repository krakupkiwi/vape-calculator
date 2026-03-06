"""
Idempotent seed script.
Populates the flavors table if empty, adds default nic bases,
and copies the default label template to /data/templates/.
"""
import json
import shutil
from pathlib import Path

from sqlmodel import Session, select

from app.database import engine
from app.models.flavor import Flavor, NicBase

FLAVORS_JSON = Path(__file__).parent.parent / "seeds" / "flavors.json"
SEEDS_TEMPLATES_DIR = Path(__file__).parent.parent / "seeds" / "templates"
DATA_TEMPLATES_DIR = Path("/data/templates")

DEFAULT_NIC_BASES = [
    NicBase(name="100mg/mL PG Nic", strength_mg=100.0, base_pg=1.0, base_vg=0.0),
    NicBase(name="100mg/mL VG Nic", strength_mg=100.0, base_pg=0.0, base_vg=1.0),
    NicBase(name="100mg/mL 50/50 Nic", strength_mg=100.0, base_pg=0.5, base_vg=0.5),
    NicBase(name="200mg/mL PG Nic", strength_mg=200.0, base_pg=1.0, base_vg=0.0),
    NicBase(name="20mg/mL PG Nic", strength_mg=20.0, base_pg=1.0, base_vg=0.0),
]


def run_seed():
    with Session(engine) as session:
        # Seed flavors only if table is empty
        count = session.exec(select(Flavor)).first()
        if count is None:
            data = json.loads(FLAVORS_JSON.read_text(encoding="utf-8"))
            for entry in data:
                session.add(Flavor(
                    name=entry["name"],
                    manufacturer=entry["manufacturer"],
                    base_pg=entry.get("base_pg", 1.0),
                    base_vg=entry.get("base_vg", 0.0),
                    density=entry.get("density", 1.0),
                    is_custom=0,
                ))
            session.commit()
            print(f"[seed] Inserted {len(data)} flavors.")
        else:
            print("[seed] Flavors table already populated — skipping.")

        # Seed nic bases only if table is empty
        nb_count = session.exec(select(NicBase)).first()
        if nb_count is None:
            for nb in DEFAULT_NIC_BASES:
                session.add(nb)
            session.commit()
            print(f"[seed] Inserted {len(DEFAULT_NIC_BASES)} nic bases.")
        else:
            print("[seed] Nic bases table already populated — skipping.")


def seed_templates():
    """Copy bundled label templates to /data/templates/ if not already present."""
    DATA_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    for src in SEEDS_TEMPLATES_DIR.glob("*.html"):
        dest = DATA_TEMPLATES_DIR / src.name
        if not dest.exists():
            shutil.copy2(src, dest)
            print(f"[seed] Copied template: {src.name}")
        else:
            print(f"[seed] Template already exists: {src.name}")


if __name__ == "__main__":
    run_seed()
    seed_templates()
