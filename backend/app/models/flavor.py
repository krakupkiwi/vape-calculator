from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Flavor(SQLModel, table=True):
    __tablename__ = "flavors"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    manufacturer: str
    abbreviation: Optional[str] = None
    base_pg: float = Field(default=1.0)
    base_vg: float = Field(default=0.0)
    density: float = Field(default=1.0)
    cost_per_ml: float = Field(default=0.0)
    notes: Optional[str] = None
    is_custom: int = Field(default=0)
    created_at: str = Field(default_factory=_now)


class NicBase(SQLModel, table=True):
    __tablename__ = "nic_bases"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    strength_mg: float
    base_pg: float
    base_vg: float
    cost_per_ml: float = Field(default=0.0)
    notes: Optional[str] = None
