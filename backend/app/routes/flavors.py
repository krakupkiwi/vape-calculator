from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select, or_

from app.database import get_session
from app.models.flavor import Flavor

router = APIRouter()


class FlavorIn(BaseModel):
    name: str
    manufacturer: str
    abbreviation: Optional[str] = None
    base_pg: float = Field(default=1.0, ge=0.0, le=1.0)
    base_vg: float = Field(default=0.0, ge=0.0, le=1.0)
    density: float = Field(default=1.0, gt=0)
    cost_per_ml: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None


class FlavorOut(BaseModel):
    id: int
    name: str
    manufacturer: str
    abbreviation: Optional[str]
    base_pg: float
    base_vg: float
    density: float
    cost_per_ml: float
    notes: Optional[str]
    is_custom: int


def _to_out(f: Flavor) -> FlavorOut:
    return FlavorOut(
        id=f.id,
        name=f.name,
        manufacturer=f.manufacturer,
        abbreviation=f.abbreviation,
        base_pg=f.base_pg,
        base_vg=f.base_vg,
        density=f.density,
        cost_per_ml=f.cost_per_ml,
        notes=f.notes,
        is_custom=f.is_custom,
    )


@router.get("/flavors", response_model=List[FlavorOut])
def list_flavors(
    q: Optional[str] = Query(default=None),
    manufacturer: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
) -> List[FlavorOut]:
    stmt = select(Flavor).order_by(Flavor.manufacturer, Flavor.name)
    if manufacturer:
        stmt = stmt.where(Flavor.manufacturer == manufacturer)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(Flavor.name.ilike(pattern), Flavor.manufacturer.ilike(pattern))
        )
    return [_to_out(f) for f in session.exec(stmt).all()]


@router.post("/flavors", response_model=FlavorOut, status_code=201)
def create_flavor(payload: FlavorIn, session: Session = Depends(get_session)) -> FlavorOut:
    # Check for duplicate name+manufacturer
    existing = session.exec(
        select(Flavor).where(Flavor.name == payload.name, Flavor.manufacturer == payload.manufacturer)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Flavor with this name and manufacturer already exists.")
    flavor = Flavor(
        name=payload.name,
        manufacturer=payload.manufacturer,
        abbreviation=payload.abbreviation,
        base_pg=payload.base_pg,
        base_vg=payload.base_vg,
        density=payload.density,
        cost_per_ml=payload.cost_per_ml,
        notes=payload.notes,
        is_custom=1,
    )
    session.add(flavor)
    session.commit()
    session.refresh(flavor)
    return _to_out(flavor)


@router.put("/flavors/{flavor_id}", response_model=FlavorOut)
def update_flavor(
    flavor_id: int,
    payload: FlavorIn,
    session: Session = Depends(get_session),
) -> FlavorOut:
    flavor = session.get(Flavor, flavor_id)
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")
    flavor.name = payload.name
    flavor.manufacturer = payload.manufacturer
    flavor.abbreviation = payload.abbreviation
    flavor.base_pg = payload.base_pg
    flavor.base_vg = payload.base_vg
    flavor.density = payload.density
    flavor.cost_per_ml = payload.cost_per_ml
    flavor.notes = payload.notes
    session.commit()
    session.refresh(flavor)
    return _to_out(flavor)


@router.delete("/flavors/{flavor_id}", status_code=204)
def delete_flavor(flavor_id: int, session: Session = Depends(get_session)) -> None:
    flavor = session.get(Flavor, flavor_id)
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")
    session.delete(flavor)
    session.commit()
