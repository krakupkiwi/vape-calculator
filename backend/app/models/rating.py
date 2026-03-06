from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RecipeRating(SQLModel, table=True):
    __tablename__ = "recipe_ratings"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipes.id")
    stars: int = Field(ge=1, le=5)
    note: Optional[str] = None
    created_at: str = Field(default_factory=_now)
