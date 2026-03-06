# Calculation Engine

The calculator is implemented as a pure Python module with no database or framework dependencies.
Location: `backend/app/engine/calculator.py`

---

## The Math

All e-liquid calculation is a linear system of constraints over a fixed total volume.
Every milliliter must be accounted for — nic base + pure PG + pure VG + flavors = batch size.

### Variables

```
V_total   = batch size in ml (user input)
V_nic     = volume of nicotine base needed
V_pg      = volume of pure PG diluent
V_vg      = volume of pure VG diluent
V_f[i]    = volume of flavor i
```

---

### Step 1 — Flavor Volumes

Each flavor is a direct percentage of the total batch:

```
V_f[i] = (flavor_pct[i] / 100) * V_total
V_flavors_total = sum(V_f[i])
```

---

### Step 2 — Nicotine Base Volume

Solve for nic base volume needed to hit target strength:

```
target_nic_mg = (V_nic * nic_base_strength_mg) / V_total

→ V_nic = (target_nic_mg * V_total) / nic_base_strength_mg
```

If `target_nic_mg == 0`, then `V_nic = 0`.

---

### Step 3 — PG/VG Accounting

Each ingredient contributes its own PG/VG content.
Pure PG and VG diluents make up the remainder.

```
pg_from_nic     = V_nic * nic_base_pg_ratio
vg_from_nic     = V_nic * nic_base_vg_ratio

pg_from_flavors = sum(V_f[i] * flavor_pg_ratio[i])
vg_from_flavors = sum(V_f[i] * flavor_vg_ratio[i])

pg_target = target_pg_ratio * V_total
vg_target = target_vg_ratio * V_total

V_pg = pg_target - pg_from_nic - pg_from_flavors
V_vg = vg_target - vg_from_nic - vg_from_flavors
```

**If V_pg or V_vg is negative:** the flavor/nic PG content exceeds the target ratio.
The engine sets the value to 0 and emits a warning to the user.

---

### Step 4 — Validation

```python
total_check = V_nic + V_pg + V_vg + V_flavors_total
assert abs(total_check - V_total) < 0.01   # floating point tolerance
```

---

### Step 5 — Weight Conversion (optional output)

Standard densities used when no flavor-specific density is set:

| Ingredient | Density (g/ml) |
|---|---|
| PG (Propylene Glycol) | 1.036 |
| VG (Vegetable Glycerin) | 1.261 |
| Flavor concentrates | 1.0 (default) |
| Nicotine base (PG-based) | ~1.036 |

```
weight_pg  = V_pg  * 1.036
weight_vg  = V_vg  * 1.261
weight_nic = V_nic * nic_base_density
weight_f[i] = V_f[i] * flavor_density[i]
```

---

### Step 6 — Cost Calculation

```
cost_nic     = V_nic * nic_cost_per_ml
cost_pg      = V_pg  * pg_cost_per_ml
cost_vg      = V_vg  * vg_cost_per_ml
cost_f[i]   = V_f[i] * flavor_cost_per_ml[i]

total_cost  = sum of all costs
cost_per_ml = total_cost / V_total
```

---

### Batch Scaling

All volumes scale linearly. No re-solving required:

```
scale_factor = new_batch_size / original_batch_size
V_scaled[x] = V_original[x] * scale_factor
```

---

## Python Implementation

```python
# backend/app/engine/calculator.py

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

    # Step 1: Flavor volumes
    flavor_vols = [(f, (f.percentage / 100) * B) for f in recipe.flavors]

    # Step 2: Nic base volume
    if recipe.nic_base_strength_mg > 0 and recipe.target_nic_mg > 0:
        v_nic = (recipe.target_nic_mg * B) / recipe.nic_base_strength_mg
    else:
        v_nic = 0.0

    # Step 3: PG/VG accounting
    pg_from_nic     = v_nic * recipe.nic_base_pg
    vg_from_nic     = v_nic * recipe.nic_base_vg
    pg_from_flavors = sum(v * f.pg_ratio for f, v in flavor_vols)
    vg_from_flavors = sum(v * f.vg_ratio for f, v in flavor_vols)

    v_pg = (recipe.target_pg * B) - pg_from_nic - pg_from_flavors
    v_vg = (recipe.target_vg * B) - vg_from_nic - vg_from_flavors

    # Step 4: Validation / clamp negatives
    if v_pg < -0.01:
        warnings.append(
            "PG from flavors/nic exceeds target PG ratio. "
            "Increase PG% or reduce flavor percentages."
        )
        v_pg = 0.0
    if v_vg < -0.01:
        warnings.append(
            "VG from flavors/nic exceeds target VG ratio. "
            "Increase VG% or reduce flavor percentages."
        )
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
            percentage=round((v_nic / B) * 100, 2)
        ))
    if v_pg > 0.001:
        ingredients.append(IngredientResult(
            name="PG (Propylene Glycol)",
            volume_ml=round(v_pg, 3),
            weight_g=round(v_pg * PG_DENSITY, 3),
            cost=round(v_pg * recipe.pg_cost_per_ml, 4),
            percentage=round((v_pg / B) * 100, 2)
        ))
    if v_vg > 0.001:
        ingredients.append(IngredientResult(
            name="VG (Vegetable Glycerin)",
            volume_ml=round(v_vg, 3),
            weight_g=round(v_vg * VG_DENSITY, 3),
            cost=round(v_vg * recipe.vg_cost_per_ml, 4),
            percentage=round((v_vg / B) * 100, 2)
        ))
    for f, v in flavor_vols:
        if v > 0.001:
            ingredients.append(IngredientResult(
                name=f.name,
                volume_ml=round(v, 3),
                weight_g=round(v * f.density, 3),
                cost=round(v * f.cost_per_ml, 4),
                percentage=round(f.percentage, 2)
            ))

    total_cost = sum(i.cost for i in ingredients)
    actual_nic = (v_nic * recipe.nic_base_strength_mg) / B if B > 0 else 0.0

    return RecipeResult(
        ingredients=ingredients,
        total_ml=round(B, 3),
        total_cost=round(total_cost, 4),
        cost_per_ml=round(total_cost / B, 4) if B > 0 else 0.0,
        actual_nic_mg=round(actual_nic, 2),
        actual_pg=round(recipe.target_pg * 100, 1),
        actual_vg=round(recipe.target_vg * 100, 1),
        warnings=warnings
    )
```

---

## Edge Cases to Handle

| Scenario | Handling |
|---|---|
| 0mg nicotine recipe | Skip nic base volume entirely |
| Flavor % total > 100% | Emit warning, let user fix |
| Flavor PG pushes V_pg negative | Clamp to 0, warn user |
| batch_size_ml = 0 | Return empty result, no division |
| nic_base_strength = 0 with target > 0 | Warn: impossible to hit nic target |
| PG ratio + VG ratio != 1.0 | Normalize before calculation |

---

## Testing

All calculation logic should be tested independently of the API layer.

```
backend/tests/test_calculator.py
```

Key test cases:
- 0mg recipe produces no nic line
- 30/70 PG/VG with 15% TFA (100% PG base) adjusts PG diluent correctly
- 100ml batch scales correctly to 500ml
- Cost calculation matches manual math
- Weight conversion uses correct densities
