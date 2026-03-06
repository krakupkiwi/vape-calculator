from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RecipeFlavor(SQLModel, table=True):
    __tablename__ = "recipe_flavors"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipes.id")
    flavor_id: Optional[int] = Field(default=None, foreign_key="flavors.id", nullable=True)
    custom_name: Optional[str] = None
    percentage: float
    pg_ratio: float = Field(default=1.0)    # stored as fraction 0.0–1.0
    vg_ratio: float = Field(default=0.0)
    density: float = Field(default=1.0)
    cost_per_ml: float = Field(default=0.0)
    sort_order: int = Field(default=0)

    recipe: Optional["Recipe"] = Relationship(back_populates="flavors")


class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    author: str = Field(default="Local User")
    description: Optional[str] = None
    notes: Optional[str] = None

    batch_size_ml: float
    target_nic_mg: float = Field(default=0.0)

    # Nic base stored inline (no nic_bases table until Phase 3)
    nic_base_strength_mg: float = Field(default=100.0)
    nic_base_pg: float = Field(default=1.0)   # fraction
    nic_base_vg: float = Field(default=0.0)
    nic_base_density: float = Field(default=1.036)
    nic_cost_per_ml: float = Field(default=0.0)

    pg_ratio: float = Field(default=0.3)      # fraction
    vg_ratio: float = Field(default=0.7)
    pg_cost_per_ml: float = Field(default=0.0)
    vg_cost_per_ml: float = Field(default=0.0)

    rating: Optional[int] = Field(default=None)
    is_public: int = Field(default=0)
    parent_id: Optional[int] = Field(default=None, foreign_key="recipes.id", nullable=True)

    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)

    flavors: List[RecipeFlavor] = Relationship(
        back_populates="recipe",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
