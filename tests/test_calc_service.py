import pytest

from app.services.calc import calculate_plan, choose_servings


class TestChooseServings:
    def test_exact_midpoint(self):
        # 1000g with 200-300 range: midpoint=250, 4 servings = 250g exactly
        servings, weight = choose_servings(1000, 200, 300)
        assert servings == 4
        assert weight == 250.0

    def test_prefers_in_range_closest_to_midpoint(self):
        # 600g with 100-200 range: midpoint=150, 4 servings=150g
        servings, weight = choose_servings(600, 100, 200)
        assert servings == 4
        assert weight == 150.0

    def test_single_serving_when_small(self):
        # 150g with 200-300 range: only 1 serving possible, out of range
        servings, weight = choose_servings(150, 200, 300)
        assert servings == 1
        assert weight == 150.0

    def test_falls_back_to_out_of_range(self):
        # 50g with 200-300 range: nothing in range, closest to min boundary
        servings, weight = choose_servings(50, 200, 300)
        assert servings == 1
        assert weight == 50.0

    def test_large_weight(self):
        # 3000g with 200-300 range: many options in range
        servings, weight = choose_servings(3000, 200, 300)
        assert 200 <= weight <= 300
        assert servings == 3000 / weight

    def test_tight_range(self):
        # 1000g with 250-250 (exact target)
        servings, weight = choose_servings(1000, 250, 250)
        assert servings == 4
        assert weight == 250.0

    def test_zero_net_weight_raises(self):
        with pytest.raises(ValueError, match="positive"):
            choose_servings(0, 200, 300)

    def test_negative_net_weight_raises(self):
        with pytest.raises(ValueError, match="positive"):
            choose_servings(-100, 200, 300)

    def test_zero_target_min_raises(self):
        with pytest.raises(ValueError, match="positive"):
            choose_servings(1000, 0, 300)

    def test_zero_target_max_raises(self):
        with pytest.raises(ValueError, match="positive"):
            choose_servings(1000, 200, 0)

    def test_min_greater_than_max_raises(self):
        with pytest.raises(ValueError, match="min must be <= target max"):
            choose_servings(1000, 400, 200)

    def test_weight_just_above_min(self):
        # 201g with 200-300 range: 1 serving at 201g is in range
        servings, weight = choose_servings(201, 200, 300)
        assert servings == 1
        assert weight == 201.0

    def test_returns_integer_servings(self):
        servings, _ = choose_servings(1305, 200, 300)
        assert isinstance(servings, int)


class TestCalculatePlan:
    def test_basic_calculation(self):
        net, servings, weight, carbs = calculate_plan(1500, 500, 100, 200, 300)
        assert net == 1000.0
        assert servings == 4
        assert weight == 250.0
        assert carbs == 25.0

    def test_with_target_servings(self):
        net, servings, weight, carbs = calculate_plan(1500, 500, 100, 200, 300, target_servings=2)
        assert net == 1000.0
        assert servings == 2
        assert weight == 500.0
        assert carbs == 50.0

    def test_target_servings_overrides_range(self):
        # Without target_servings: 1305g, 200-300 range -> 5 servings
        _, servings_auto, _, _ = calculate_plan(3545, 2240, 230, 200, 300)
        assert servings_auto == 5

        # With target_servings=4: overrides to 4
        _, servings_fixed, weight, carbs = calculate_plan(3545, 2240, 230, 200, 300, target_servings=4)
        assert servings_fixed == 4
        assert weight == pytest.approx(326.25)
        assert carbs == pytest.approx(57.5)

    def test_target_servings_one(self):
        net, servings, weight, carbs = calculate_plan(1000, 200, 80, 200, 300, target_servings=1)
        assert net == 800.0
        assert servings == 1
        assert weight == 800.0
        assert carbs == 80.0

    def test_target_servings_many(self):
        net, servings, weight, carbs = calculate_plan(1000, 200, 80, 200, 300, target_servings=10)
        assert servings == 10
        assert weight == 80.0
        assert carbs == 8.0

    def test_net_weight_zero_raises(self):
        with pytest.raises(ValueError, match="greater than pan weight"):
            calculate_plan(500, 500, 100, 200, 300)

    def test_net_weight_negative_raises(self):
        with pytest.raises(ValueError, match="greater than pan weight"):
            calculate_plan(300, 500, 100, 200, 300)

    def test_zero_carbs(self):
        net, servings, weight, carbs = calculate_plan(1000, 200, 0, 200, 300)
        assert carbs == 0.0

    def test_target_servings_none_uses_range(self):
        result_none = calculate_plan(1500, 500, 100, 200, 300, target_servings=None)
        result_default = calculate_plan(1500, 500, 100, 200, 300)
        assert result_none == result_default
