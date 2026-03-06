from dataclasses import dataclass, field
from typing import List


@dataclass
class FlavorInput:
    name: str
    percentage: float       # 0–100
    pg_ratio: float         # 0.0–1.0 (default 1.0 for most concentrates)
    vg_ratio: float         # 0.0–1.0
    density: float = 1.0
    cost_per_ml: float = 0.0


@dataclass
class RecipeInput:
    batch_size_ml: float
    target_nic_mg: float
    nic_base_strength_mg: float
    nic_base_pg: float
    nic_base_vg: float
    nic_base_density: float
    nic_cost_per_ml: float
    target_pg: float            # 0.0–1.0
    target_vg: float
    pg_cost_per_ml: float
    vg_cost_per_ml: float
    flavors: List[FlavorInput] = field(default_factory=list)


@dataclass
class IngredientResult:
    name: str
    volume_ml: float
    weight_g: float
    cost: float
    percentage: float


@dataclass
class RecipeResult:
    ingredients: List[IngredientResult]
    total_ml: float
    total_cost: float
    cost_per_ml: float
    actual_nic_mg: float
    actual_pg: float
    actual_vg: float
    warnings: List[str]


def calculate(recipe: RecipeInput) -> RecipeResult:
    B = recipe.batch_size_ml
    warnings = []

    if B <= 0:
        return RecipeResult(
            ingredients=[],
            total_ml=0.0,
            total_cost=0.0,
            cost_per_ml=0.0,
            actual_nic_mg=0.0,
            actual_pg=0.0,
            actual_vg=0.0,
            warnings=["Batch size must be greater than 0."],
        )

    # Normalize PG/VG ratio if they don't sum to 1
    pg_vg_sum = recipe.target_pg + recipe.target_vg
    if pg_vg_sum > 0 and abs(pg_vg_sum - 1.0) > 0.001:
        t_pg = recipe.target_pg / pg_vg_sum
        t_vg = recipe.target_vg / pg_vg_sum
        warnings.append(
            f"PG/VG ratio normalized from {recipe.target_pg:.2f}/{recipe.target_vg:.2f} "
            f"to {t_pg:.2f}/{t_vg:.2f}."
        )
    else:
        t_pg = recipe.target_pg
        t_vg = recipe.target_vg

    # Validate total flavor percentage
    total_flavor_pct = sum(f.percentage for f in recipe.flavors)
    if total_flavor_pct > 100:
        warnings.append(
            f"Total flavor percentage ({total_flavor_pct:.1f}%) exceeds 100%. "
            "Reduce flavor percentages."
        )

    # Step 1: Flavor volumes
    flavor_vols = [(f, (f.percentage / 100) * B) for f in recipe.flavors]

    # Step 2: Nic base volume
    if recipe.nic_base_strength_mg > 0 and recipe.target_nic_mg > 0:
        v_nic = (recipe.target_nic_mg * B) / recipe.nic_base_strength_mg
    elif recipe.nic_base_strength_mg == 0 and recipe.target_nic_mg > 0:
        warnings.append(
            "Nic base strength is 0 but target nicotine is > 0. "
            "Cannot achieve target nicotine strength."
        )
        v_nic = 0.0
    else:
        v_nic = 0.0

    # Step 3: PG/VG accounting
    pg_from_nic = v_nic * recipe.nic_base_pg
    vg_from_nic = v_nic * recipe.nic_base_vg
    pg_from_flavors = sum(v * f.pg_ratio for f, v in flavor_vols)
    vg_from_flavors = sum(v * f.vg_ratio for f, v in flavor_vols)

    v_pg = (t_pg * B) - pg_from_nic - pg_from_flavors
    v_vg = (t_vg * B) - vg_from_nic - vg_from_flavors

    # Step 4: Clamp negatives, emit warnings
    if v_pg < -0.01:
        warnings.append(
            "PG from flavors/nic exceeds target PG ratio. "
            "Increase PG% or reduce flavor percentages."
        )
        v_pg = 0.0
    elif v_pg < 0:
        v_pg = 0.0

    if v_vg < -0.01:
        warnings.append(
            "VG from flavors/nic exceeds target VG ratio. "
            "Increase VG% or reduce flavor percentages."
        )
        v_vg = 0.0
    elif v_vg < 0:
        v_vg = 0.0

    PG_DENSITY = 1.036
    VG_DENSITY = 1.261

    ingredients: List[IngredientResult] = []

    if v_nic > 0.001:
        ingredients.append(IngredientResult(
            name=f"Nicotine Base ({recipe.nic_base_strength_mg}mg/ml)",
            volume_ml=round(v_nic, 3),
            weight_g=round(v_nic * recipe.nic_base_density, 3),
            cost=round(v_nic * recipe.nic_cost_per_ml, 4),
            percentage=round((v_nic / B) * 100, 2),
        ))
    if v_pg > 0.001:
        ingredients.append(IngredientResult(
            name="PG (Propylene Glycol)",
            volume_ml=round(v_pg, 3),
            weight_g=round(v_pg * PG_DENSITY, 3),
            cost=round(v_pg * recipe.pg_cost_per_ml, 4),
            percentage=round((v_pg / B) * 100, 2),
        ))
    if v_vg > 0.001:
        ingredients.append(IngredientResult(
            name="VG (Vegetable Glycerin)",
            volume_ml=round(v_vg, 3),
            weight_g=round(v_vg * VG_DENSITY, 3),
            cost=round(v_vg * recipe.vg_cost_per_ml, 4),
            percentage=round((v_vg / B) * 100, 2),
        ))
    for f, v in flavor_vols:
        if v > 0.001:
            ingredients.append(IngredientResult(
                name=f.name,
                volume_ml=round(v, 3),
                weight_g=round(v * f.density, 3),
                cost=round(v * f.cost_per_ml, 4),
                percentage=round(f.percentage, 2),
            ))

    total_cost = sum(i.cost for i in ingredients)
    actual_nic = (v_nic * recipe.nic_base_strength_mg) / B if B > 0 else 0.0

    return RecipeResult(
        ingredients=ingredients,
        total_ml=round(B, 3),
        total_cost=round(total_cost, 4),
        cost_per_ml=round(total_cost / B, 4) if B > 0 else 0.0,
        actual_nic_mg=round(actual_nic, 2),
        actual_pg=round(t_pg * 100, 1),
        actual_vg=round(t_vg * 100, 1),
        warnings=warnings,
    )
