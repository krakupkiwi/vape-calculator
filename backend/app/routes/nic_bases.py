from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.database import get_session
from app.models.flavor import NicBase

router = APIRouter()


class NicBaseIn(BaseModel):
    name: str
    strength_mg: float = Field(gt=0)
    base_pg: float = Field(ge=0.0, le=1.0)
    base_vg: float = Field(ge=0.0, le=1.0)
    cost_per_ml: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None


class NicBaseOut(BaseModel):
    id: int
    name: str
    strength_mg: float
    base_pg: float
    base_vg: float
    cost_per_ml: float
    notes: Optional[str]


def _to_out(nb: NicBase) -> NicBaseOut:
    return NicBaseOut(
        id=nb.id,
        name=nb.name,
        strength_mg=nb.strength_mg,
        base_pg=nb.base_pg,
        base_vg=nb.base_vg,
        cost_per_ml=nb.cost_per_ml,
        notes=nb.notes,
    )


@router.get("/nic-bases", response_model=List[NicBaseOut])
def list_nic_bases(session: Session = Depends(get_session)) -> List[NicBaseOut]:
    return [_to_out(nb) for nb in session.exec(select(NicBase).order_by(NicBase.name)).all()]


@router.post("/nic-bases", response_model=NicBaseOut, status_code=201)
def create_nic_base(payload: NicBaseIn, session: Session = Depends(get_session)) -> NicBaseOut:
    nb = NicBase(**payload.model_dump())
    session.add(nb)
    session.commit()
    session.refresh(nb)
    return _to_out(nb)


@router.put("/nic-bases/{nb_id}", response_model=NicBaseOut)
def update_nic_base(
    nb_id: int,
    payload: NicBaseIn,
    session: Session = Depends(get_session),
) -> NicBaseOut:
    nb = session.get(NicBase, nb_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Nic base not found")
    for k, v in payload.model_dump().items():
        setattr(nb, k, v)
    session.commit()
    session.refresh(nb)
    return _to_out(nb)


@router.delete("/nic-bases/{nb_id}", status_code=204)
def delete_nic_base(nb_id: int, session: Session = Depends(get_session)) -> None:
    nb = session.get(NicBase, nb_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Nic base not found")
    session.delete(nb)
    session.commit()
