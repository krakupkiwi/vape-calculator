from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List

from app.engine.calculator import (
    calculate,
    FlavorInput,
    RecipeInput,
)

router = APIRouter()


class FlavorPayload(BaseModel):
    name: str
    percentage: float = Field(ge=0, le=100)
    pg_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    vg_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    density: float = Field(default=1.0, gt=0)
    cost_per_ml: float = Field(default=0.0, ge=0)


class CalculateRequest(BaseModel):
    batch_size_ml: float = Field(gt=0)
    target_nic_mg: float = Field(default=0.0, ge=0)
    nic_base_strength_mg: float = Field(default=100.0, ge=0)
    nic_base_pg: float = Field(default=1.0, ge=0.0, le=1.0)
    nic_base_vg: float = Field(default=0.0, ge=0.0, le=1.0)
    nic_base_density: float = Field(default=1.036, gt=0)
    nic_cost_per_ml: float = Field(default=0.0, ge=0)
    target_pg: float = Field(default=0.3, ge=0.0, le=1.0)
    target_vg: float = Field(default=0.7, ge=0.0, le=1.0)
    pg_cost_per_ml: float = Field(default=0.0, ge=0)
    vg_cost_per_ml: float = Field(default=0.0, ge=0)
    flavors: List[FlavorPayload] = Field(default_factory=list)


class IngredientResponse(BaseModel):
    name: str
    volume_ml: float
    weight_g: float
    cost: float
    percentage: float


class CalculateResponse(BaseModel):
    ingredients: List[IngredientResponse]
    total_ml: float
    total_cost: float
    cost_per_ml: float
    actual_nic_mg: float
    actual_pg: float
    actual_vg: float
    warnings: List[str]


@router.post("/calculate", response_model=CalculateResponse)
def calculate_recipe(payload: CalculateRequest) -> CalculateResponse:
    recipe = RecipeInput(
        batch_size_ml=payload.batch_size_ml,
        target_nic_mg=payload.target_nic_mg,
        nic_base_strength_mg=payload.nic_base_strength_mg,
        nic_base_pg=payload.nic_base_pg,
        nic_base_vg=payload.nic_base_vg,
        nic_base_density=payload.nic_base_density,
        nic_cost_per_ml=payload.nic_cost_per_ml,
        target_pg=payload.target_pg,
        target_vg=payload.target_vg,
        pg_cost_per_ml=payload.pg_cost_per_ml,
        vg_cost_per_ml=payload.vg_cost_per_ml,
        flavors=[
            FlavorInput(
                name=f.name,
                percentage=f.percentage,
                pg_ratio=f.pg_ratio,
                vg_ratio=f.vg_ratio,
                density=f.density,
                cost_per_ml=f.cost_per_ml,
            )
            for f in payload.flavors
        ],
    )
    result = calculate(recipe)
    return CalculateResponse(
        ingredients=[
            IngredientResponse(
                name=i.name,
                volume_ml=i.volume_ml,
                weight_g=i.weight_g,
                cost=i.cost,
                percentage=i.percentage,
            )
            for i in result.ingredients
        ],
        total_ml=result.total_ml,
        total_cost=result.total_cost,
        cost_per_ml=result.cost_per_ml,
        actual_nic_mg=result.actual_nic_mg,
        actual_pg=result.actual_pg,
        actual_vg=result.actual_vg,
        warnings=result.warnings,
    )
