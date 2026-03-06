from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.database import get_session
from app.models.recipe import Recipe, RecipeFlavor
from app.models.rating import RecipeRating

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class FlavorIn(BaseModel):
    name: str
    percentage: float = Field(ge=0, le=100)
    pg_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    vg_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    density: float = Field(default=1.0, gt=0)
    cost_per_ml: float = Field(default=0.0, ge=0)
    sort_order: int = Field(default=0)


class RecipeIn(BaseModel):
    name: str
    description: Optional[str] = None
    notes: Optional[str] = None
    batch_size_ml: float = Field(gt=0)
    target_nic_mg: float = Field(default=0.0, ge=0)
    nic_base_strength_mg: float = Field(default=100.0, ge=0)
    nic_base_pg: float = Field(default=1.0, ge=0.0, le=1.0)
    nic_base_vg: float = Field(default=0.0, ge=0.0, le=1.0)
    nic_base_density: float = Field(default=1.036, gt=0)
    nic_cost_per_ml: float = Field(default=0.0, ge=0)
    pg_ratio: float = Field(default=0.3, ge=0.0, le=1.0)
    vg_ratio: float = Field(default=0.7, ge=0.0, le=1.0)
    pg_cost_per_ml: float = Field(default=0.0, ge=0)
    vg_cost_per_ml: float = Field(default=0.0, ge=0)
    flavors: List[FlavorIn] = Field(default_factory=list)


class FlavorOut(BaseModel):
    id: int
    name: str
    percentage: float
    pg_ratio: float
    vg_ratio: float
    density: float
    cost_per_ml: float
    sort_order: int


class RecipeOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    notes: Optional[str]
    batch_size_ml: float
    target_nic_mg: float
    nic_base_strength_mg: float
    nic_base_pg: float
    nic_base_vg: float
    nic_base_density: float
    nic_cost_per_ml: float
    pg_ratio: float
    vg_ratio: float
    pg_cost_per_ml: float
    vg_cost_per_ml: float
    created_at: str
    updated_at: str
    rating: Optional[int] = None
    flavors: List[FlavorOut]


class RatingIn(BaseModel):
    stars: int = Field(ge=1, le=5)
    note: Optional[str] = None


class RatingOut(BaseModel):
    id: int
    stars: int
    note: Optional[str]
    created_at: str


class RecipeSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    batch_size_ml: float
    target_nic_mg: float
    pg_ratio: float
    vg_ratio: float
    created_at: str
    updated_at: str
    flavor_count: int
    rating: Optional[int] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flavor_name(f: RecipeFlavor) -> str:
    return f.custom_name or ""


def _recipe_to_out(recipe: Recipe) -> RecipeOut:
    return RecipeOut(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        notes=recipe.notes,
        batch_size_ml=recipe.batch_size_ml,
        target_nic_mg=recipe.target_nic_mg,
        nic_base_strength_mg=recipe.nic_base_strength_mg,
        nic_base_pg=recipe.nic_base_pg,
        nic_base_vg=recipe.nic_base_vg,
        nic_base_density=recipe.nic_base_density,
        nic_cost_per_ml=recipe.nic_cost_per_ml,
        pg_ratio=recipe.pg_ratio,
        vg_ratio=recipe.vg_ratio,
        pg_cost_per_ml=recipe.pg_cost_per_ml,
        vg_cost_per_ml=recipe.vg_cost_per_ml,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        rating=recipe.rating,
        flavors=[
            FlavorOut(
                id=f.id,
                name=_flavor_name(f),
                percentage=f.percentage,
                pg_ratio=f.pg_ratio,
                vg_ratio=f.vg_ratio,
                density=f.density,
                cost_per_ml=f.cost_per_ml,
                sort_order=f.sort_order,
            )
            for f in sorted(recipe.flavors, key=lambda x: x.sort_order)
        ],
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/recipes", response_model=RecipeOut, status_code=201)
def create_recipe(payload: RecipeIn, session: Session = Depends(get_session)) -> RecipeOut:
    recipe = Recipe(
        name=payload.name,
        description=payload.description,
        notes=payload.notes,
        batch_size_ml=payload.batch_size_ml,
        target_nic_mg=payload.target_nic_mg,
        nic_base_strength_mg=payload.nic_base_strength_mg,
        nic_base_pg=payload.nic_base_pg,
        nic_base_vg=payload.nic_base_vg,
        nic_base_density=payload.nic_base_density,
        nic_cost_per_ml=payload.nic_cost_per_ml,
        pg_ratio=payload.pg_ratio,
        vg_ratio=payload.vg_ratio,
        pg_cost_per_ml=payload.pg_cost_per_ml,
        vg_cost_per_ml=payload.vg_cost_per_ml,
    )
    session.add(recipe)
    session.flush()  # get recipe.id before adding flavors

    for i, f in enumerate(payload.flavors):
        session.add(RecipeFlavor(
            recipe_id=recipe.id,
            custom_name=f.name,
            percentage=f.percentage,
            pg_ratio=f.pg_ratio,
            vg_ratio=f.vg_ratio,
            density=f.density,
            cost_per_ml=f.cost_per_ml,
            sort_order=f.sort_order if f.sort_order else i,
        ))

    session.commit()
    session.refresh(recipe)
    return _recipe_to_out(recipe)


@router.get("/recipes", response_model=List[RecipeSummary])
def list_recipes(
    sort: str = "date",
    min_rating: Optional[int] = None,
    session: Session = Depends(get_session),
) -> List[RecipeSummary]:
    stmt = select(Recipe)
    if min_rating is not None:
        stmt = stmt.where(Recipe.rating >= min_rating)
    if sort == "name":
        stmt = stmt.order_by(Recipe.name)
    elif sort == "rating":
        stmt = stmt.order_by(Recipe.rating.desc())
    else:
        stmt = stmt.order_by(Recipe.created_at.desc())

    recipes = session.exec(stmt).all()
    return [
        RecipeSummary(
            id=r.id,
            name=r.name,
            description=r.description,
            batch_size_ml=r.batch_size_ml,
            target_nic_mg=r.target_nic_mg,
            pg_ratio=r.pg_ratio,
            vg_ratio=r.vg_ratio,
            created_at=r.created_at,
            updated_at=r.updated_at,
            flavor_count=len(r.flavors),
            rating=r.rating,
        )
        for r in recipes
    ]


@router.get("/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, session: Session = Depends(get_session)) -> RecipeOut:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return _recipe_to_out(recipe)


@router.put("/recipes/{recipe_id}", response_model=RecipeOut)
def update_recipe(
    recipe_id: int,
    payload: RecipeIn,
    session: Session = Depends(get_session),
) -> RecipeOut:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.name = payload.name
    recipe.description = payload.description
    recipe.notes = payload.notes
    recipe.batch_size_ml = payload.batch_size_ml
    recipe.target_nic_mg = payload.target_nic_mg
    recipe.nic_base_strength_mg = payload.nic_base_strength_mg
    recipe.nic_base_pg = payload.nic_base_pg
    recipe.nic_base_vg = payload.nic_base_vg
    recipe.nic_base_density = payload.nic_base_density
    recipe.nic_cost_per_ml = payload.nic_cost_per_ml
    recipe.pg_ratio = payload.pg_ratio
    recipe.vg_ratio = payload.vg_ratio
    recipe.pg_cost_per_ml = payload.pg_cost_per_ml
    recipe.vg_cost_per_ml = payload.vg_cost_per_ml
    recipe.updated_at = _now()

    # Replace flavors: delete old, insert new
    for f in list(recipe.flavors):
        session.delete(f)
    session.flush()

    for i, f in enumerate(payload.flavors):
        session.add(RecipeFlavor(
            recipe_id=recipe.id,
            custom_name=f.name,
            percentage=f.percentage,
            pg_ratio=f.pg_ratio,
            vg_ratio=f.vg_ratio,
            density=f.density,
            cost_per_ml=f.cost_per_ml,
            sort_order=f.sort_order if f.sort_order else i,
        ))

    session.commit()
    session.refresh(recipe)
    return _recipe_to_out(recipe)


@router.delete("/recipes/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, session: Session = Depends(get_session)) -> None:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    session.delete(recipe)
    session.commit()


@router.post("/recipes/{recipe_id}/clone", response_model=RecipeOut, status_code=201)
def clone_recipe(recipe_id: int, session: Session = Depends(get_session)) -> RecipeOut:
    original = session.get(Recipe, recipe_id)
    if not original:
        raise HTTPException(status_code=404, detail="Recipe not found")

    clone = Recipe(
        name=f"{original.name} (copy)",
        description=original.description,
        notes=original.notes,
        batch_size_ml=original.batch_size_ml,
        target_nic_mg=original.target_nic_mg,
        nic_base_strength_mg=original.nic_base_strength_mg,
        nic_base_pg=original.nic_base_pg,
        nic_base_vg=original.nic_base_vg,
        nic_base_density=original.nic_base_density,
        nic_cost_per_ml=original.nic_cost_per_ml,
        pg_ratio=original.pg_ratio,
        vg_ratio=original.vg_ratio,
        pg_cost_per_ml=original.pg_cost_per_ml,
        vg_cost_per_ml=original.vg_cost_per_ml,
        parent_id=original.id,
    )
    session.add(clone)
    session.flush()

    for f in sorted(original.flavors, key=lambda x: x.sort_order):
        session.add(RecipeFlavor(
            recipe_id=clone.id,
            custom_name=f.custom_name,
            percentage=f.percentage,
            pg_ratio=f.pg_ratio,
            vg_ratio=f.vg_ratio,
            density=f.density,
            cost_per_ml=f.cost_per_ml,
            sort_order=f.sort_order,
        ))

    session.commit()
    session.refresh(clone)
    return _recipe_to_out(clone)

@router.get("/recipes/{recipe_id}/ratings", response_model=List[RatingOut])
def list_ratings(recipe_id: int, session: Session = Depends(get_session)) -> List[RatingOut]:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    ratings = session.exec(
        select(RecipeRating)
        .where(RecipeRating.recipe_id == recipe_id)
        .order_by(RecipeRating.created_at.desc())
    ).all()
    return [RatingOut(id=r.id, stars=r.stars, note=r.note, created_at=r.created_at) for r in ratings]


@router.post("/recipes/{recipe_id}/ratings", response_model=RatingOut, status_code=201)
def add_rating(
    recipe_id: int,
    payload: RatingIn,
    session: Session = Depends(get_session),
) -> RatingOut:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    rating = RecipeRating(recipe_id=recipe_id, stars=payload.stars, note=payload.note)
    session.add(rating)
    # Update the denormalized rating on the recipe
    recipe.rating = payload.stars
    recipe.updated_at = _now()
    session.commit()
    session.refresh(rating)
    return RatingOut(id=rating.id, stars=rating.stars, note=rating.note, created_at=rating.created_at)
