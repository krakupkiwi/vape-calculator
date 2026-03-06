"""
Unit tests for the calculation engine.
All tests are independent of FastAPI, SQLModel, and any other framework.
"""
import pytest
from app.engine.calculator import (
    calculate,
    FlavorInput,
    RecipeInput,
    RecipeResult,
)


def make_recipe(**overrides) -> RecipeInput:
    """Return a base 100ml 0mg 30/70 recipe with no flavors."""
    defaults = dict(
        batch_size_ml=100.0,
        target_nic_mg=0.0,
        nic_base_strength_mg=100.0,
        nic_base_pg=1.0,
        nic_base_vg=0.0,
        nic_base_density=1.036,
        nic_cost_per_ml=0.0,
        target_pg=0.3,
        target_vg=0.7,
        pg_cost_per_ml=0.0,
        vg_cost_per_ml=0.0,
        flavors=[],
    )
    defaults.update(overrides)
    return RecipeInput(**defaults)


# ---------------------------------------------------------------------------
# Milestone scenario: 100ml, 3mg, 30/70, 15% TFA Strawberry (100% PG)
# ---------------------------------------------------------------------------

class TestMilestoneRecipe:
    def test_volumes_sum_to_batch(self):
        recipe = make_recipe(
            target_nic_mg=3.0,
            nic_base_strength_mg=100.0,
            nic_base_pg=1.0,
            nic_base_vg=0.0,
            target_pg=0.3,
            target_vg=0.7,
            flavors=[FlavorInput(name="TFA Strawberry", percentage=15.0, pg_ratio=1.0, vg_ratio=0.0)],
        )
        result = calculate(recipe)
        total = sum(i.volume_ml for i in result.ingredients)
        assert abs(total - 100.0) < 0.05

    def test_nic_volume(self):
        # 3mg target / 100mg base = 3ml nic base
        recipe = make_recipe(
            target_nic_mg=3.0,
            nic_base_strength_mg=100.0,
            target_pg=0.3,
            target_vg=0.7,
            flavors=[FlavorInput(name="TFA Strawberry", percentage=15.0, pg_ratio=1.0, vg_ratio=0.0)],
        )
        result = calculate(recipe)
        nic_line = next((i for i in result.ingredients if "Nicotine" in i.name), None)
        assert nic_line is not None
        assert abs(nic_line.volume_ml - 3.0) < 0.001

    def test_flavor_volume(self):
        recipe = make_recipe(
            target_nic_mg=3.0,
            nic_base_strength_mg=100.0,
            target_pg=0.3,
            target_vg=0.7,
            flavors=[FlavorInput(name="TFA Strawberry", percentage=15.0, pg_ratio=1.0, vg_ratio=0.0)],
        )
        result = calculate(recipe)
        flavor_line = next((i for i in result.ingredients if i.name == "TFA Strawberry"), None)
        assert flavor_line is not None
        assert abs(flavor_line.volume_ml - 15.0) < 0.001

    def test_pg_vg_volumes(self):
        """
        100ml, 3mg (3ml nic @ 100% PG), 15ml TFA (100% PG), 30/70 ratio
        pg_needed = 30ml - 3ml(nic) - 15ml(flavor) = 12ml
        vg_needed = 70ml - 0ml(nic) - 0ml(flavor) = 70ml
        """
        recipe = make_recipe(
            target_nic_mg=3.0,
            nic_base_strength_mg=100.0,
            nic_base_pg=1.0,
            nic_base_vg=0.0,
            target_pg=0.3,
            target_vg=0.7,
            flavors=[FlavorInput(name="TFA Strawberry", percentage=15.0, pg_ratio=1.0, vg_ratio=0.0)],
        )
        result = calculate(recipe)
        pg_line = next((i for i in result.ingredients if "Propylene" in i.name), None)
        vg_line = next((i for i in result.ingredients if "Vegetable" in i.name), None)
        assert pg_line is not None
        assert abs(pg_line.volume_ml - 12.0) < 0.001
        assert vg_line is not None
        assert abs(vg_line.volume_ml - 70.0) < 0.001

    def test_no_warnings(self):
        recipe = make_recipe(
            target_nic_mg=3.0,
            nic_base_strength_mg=100.0,
            target_pg=0.3,
            target_vg=0.7,
            flavors=[FlavorInput(name="TFA Strawberry", percentage=15.0, pg_ratio=1.0, vg_ratio=0.0)],
        )
        result = calculate(recipe)
        assert result.warnings == []


# ---------------------------------------------------------------------------
# Zero nicotine recipe
# ---------------------------------------------------------------------------

class TestZeroNic:
    def test_no_nic_line(self):
        recipe = make_recipe(target_nic_mg=0.0)
        result = calculate(recipe)
        nic_line = next((i for i in result.ingredients if "Nicotine" in i.name), None)
        assert nic_line is None

    def test_pg_vg_fill_batch(self):
        recipe = make_recipe(target_nic_mg=0.0, target_pg=0.3, target_vg=0.7)
        result = calculate(recipe)
        total = sum(i.volume_ml for i in result.ingredients)
        assert abs(total - 100.0) < 0.05


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_zero_batch_size_returns_warning(self):
        recipe = make_recipe(batch_size_ml=0.0)
        # batch_size_ml=0 triggers the guard; use RecipeInput directly
        r = RecipeInput(
            batch_size_ml=0.0,
            target_nic_mg=3.0,
            nic_base_strength_mg=100.0,
            nic_base_pg=1.0,
            nic_base_vg=0.0,
            nic_base_density=1.036,
            nic_cost_per_ml=0.0,
            target_pg=0.3,
            target_vg=0.7,
            pg_cost_per_ml=0.0,
            vg_cost_per_ml=0.0,
            flavors=[],
        )
        result = calculate(r)
        assert result.total_ml == 0.0
        assert len(result.warnings) > 0

    def test_pg_negative_clamped_with_warning(self):
        """High-PG flavors pushing PG diluent negative should clamp and warn."""
        recipe = make_recipe(
            target_nic_mg=0.0,
            target_pg=0.1,   # only 10ml PG budget
            target_vg=0.9,
            flavors=[
                FlavorInput(name="Flavor A", percentage=20.0, pg_ratio=1.0, vg_ratio=0.0),
                FlavorInput(name="Flavor B", percentage=20.0, pg_ratio=1.0, vg_ratio=0.0),
            ],
        )
        result = calculate(recipe)
        pg_line = next((i for i in result.ingredients if "Propylene" in i.name), None)
        assert pg_line is None or pg_line.volume_ml == 0.0
        assert any("PG" in w for w in result.warnings)

    def test_vg_negative_clamped_with_warning(self):
        recipe = make_recipe(
            target_nic_mg=0.0,
            target_pg=0.9,
            target_vg=0.1,   # only 10ml VG budget
            flavors=[
                FlavorInput(name="Flavor A", percentage=20.0, pg_ratio=0.0, vg_ratio=1.0),
                FlavorInput(name="Flavor B", percentage=20.0, pg_ratio=0.0, vg_ratio=1.0),
            ],
        )
        result = calculate(recipe)
        vg_line = next((i for i in result.ingredients if "Vegetable" in i.name), None)
        assert vg_line is None or vg_line.volume_ml == 0.0
        assert any("VG" in w for w in result.warnings)

    def test_nic_base_zero_strength_with_nonzero_target_warns(self):
        r = RecipeInput(
            batch_size_ml=100.0,
            target_nic_mg=3.0,
            nic_base_strength_mg=0.0,
            nic_base_pg=1.0,
            nic_base_vg=0.0,
            nic_base_density=1.036,
            nic_cost_per_ml=0.0,
            target_pg=0.3,
            target_vg=0.7,
            pg_cost_per_ml=0.0,
            vg_cost_per_ml=0.0,
            flavors=[],
        )
        result = calculate(r)
        assert any("Cannot achieve" in w or "strength is 0" in w for w in result.warnings)

    def test_total_flavor_over_100_warns(self):
        recipe = make_recipe(
            flavors=[
                FlavorInput(name="A", percentage=60.0, pg_ratio=1.0, vg_ratio=0.0),
                FlavorInput(name="B", percentage=60.0, pg_ratio=1.0, vg_ratio=0.0),
            ]
        )
        result = calculate(recipe)
        assert any("100%" in w or "exceed" in w.lower() for w in result.warnings)

    def test_pg_vg_ratio_normalization(self):
        """Non-summing PG/VG ratios should be normalized and warn."""
        r = RecipeInput(
            batch_size_ml=100.0,
            target_nic_mg=0.0,
            nic_base_strength_mg=100.0,
            nic_base_pg=1.0,
            nic_base_vg=0.0,
            nic_base_density=1.036,
            nic_cost_per_ml=0.0,
            target_pg=0.4,
            target_vg=0.4,   # sums to 0.8, not 1.0
            pg_cost_per_ml=0.0,
            vg_cost_per_ml=0.0,
            flavors=[],
        )
        result = calculate(r)
        assert any("normalized" in w.lower() for w in result.warnings)


# ---------------------------------------------------------------------------
# Batch scaling
# ---------------------------------------------------------------------------

class TestBatchScaling:
    def _base_result(self, batch):
        recipe = make_recipe(
            batch_size_ml=batch,
            target_nic_mg=3.0,
            nic_base_strength_mg=100.0,
            nic_base_pg=1.0,
            nic_base_vg=0.0,
            target_pg=0.3,
            target_vg=0.7,
            flavors=[FlavorInput(name="TFA Strawberry", percentage=15.0, pg_ratio=1.0, vg_ratio=0.0)],
        )
        return calculate(recipe)

    def test_100ml_to_500ml_scales_linearly(self):
        r100 = self._base_result(100.0)
        r500 = self._base_result(500.0)

        def vol(result, name_fragment):
            line = next((i for i in result.ingredients if name_fragment in i.name), None)
            return line.volume_ml if line else 0.0

        assert abs(vol(r500, "TFA") - vol(r100, "TFA") * 5) < 0.01
        assert abs(vol(r500, "Nicotine") - vol(r100, "Nicotine") * 5) < 0.01
        assert abs(vol(r500, "Propylene") - vol(r100, "Propylene") * 5) < 0.01
        assert abs(vol(r500, "Vegetable") - vol(r100, "Vegetable") * 5) < 0.01


# ---------------------------------------------------------------------------
# Weight conversion
# ---------------------------------------------------------------------------

class TestWeightConversion:
    def test_pg_density(self):
        recipe = make_recipe(target_nic_mg=0.0, target_pg=1.0, target_vg=0.0)
        result = calculate(recipe)
        pg_line = next((i for i in result.ingredients if "Propylene" in i.name), None)
        assert pg_line is not None
        expected_weight = round(100.0 * 1.036, 3)
        assert abs(pg_line.weight_g - expected_weight) < 0.01

    def test_vg_density(self):
        recipe = make_recipe(target_nic_mg=0.0, target_pg=0.0, target_vg=1.0)
        result = calculate(recipe)
        vg_line = next((i for i in result.ingredients if "Vegetable" in i.name), None)
        assert vg_line is not None
        expected_weight = round(100.0 * 1.261, 3)
        assert abs(vg_line.weight_g - expected_weight) < 0.01


# ---------------------------------------------------------------------------
# Cost calculation
# ---------------------------------------------------------------------------

class TestCostCalculation:
    def test_cost_per_ml_matches_manual(self):
        recipe = make_recipe(
            target_nic_mg=0.0,
            target_pg=0.3,
            target_vg=0.7,
            pg_cost_per_ml=0.01,
            vg_cost_per_ml=0.02,
            flavors=[
                FlavorInput(name="Flavor", percentage=10.0, pg_ratio=1.0, vg_ratio=0.0, cost_per_ml=0.10),
            ],
        )
        result = calculate(recipe)
        # Manual: 20ml PG * 0.01 + 70ml VG * 0.02 + 10ml Flavor * 0.10
        expected = 20 * 0.01 + 70 * 0.02 + 10 * 0.10
        assert abs(result.total_cost - expected) < 0.001
        assert abs(result.cost_per_ml - expected / 100) < 0.0001
