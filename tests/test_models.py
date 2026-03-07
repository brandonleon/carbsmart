import pytest
from pydantic import ValidationError

from app.models import CalcRequest, CalcResponse, Pan, PanCreate, PanUpdate


class TestPanCreate:
    def test_valid(self):
        pan = PanCreate(name="Sheet Pan", weight_grams=500)
        assert pan.name == "Sheet Pan"
        assert pan.weight_grams == 500
        assert pan.capacity_label is None
        assert pan.notes is None

    def test_with_optional_fields(self):
        pan = PanCreate(name="Stock Pot", weight_grams=2240, capacity_label="6 L", notes="Big one")
        assert pan.capacity_label == "6 L"
        assert pan.notes == "Big one"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            PanCreate(name="", weight_grams=500)

    def test_zero_weight_rejected(self):
        with pytest.raises(ValidationError):
            PanCreate(name="Pan", weight_grams=0)

    def test_negative_weight_rejected(self):
        with pytest.raises(ValidationError):
            PanCreate(name="Pan", weight_grams=-100)


class TestPanUpdate:
    def test_partial_update(self):
        update = PanUpdate(name="New Name")
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"name": "New Name"}

    def test_empty_update(self):
        update = PanUpdate()
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {}

    def test_zero_weight_rejected(self):
        with pytest.raises(ValidationError):
            PanUpdate(weight_grams=0)


class TestPan:
    def test_from_attributes(self):
        pan = Pan(id=1, name="Test", weight_grams=100)
        assert pan.id == 1


class TestCalcRequest:
    def test_defaults(self):
        req = CalcRequest(total_weight_grams=1000, pan_id=1, total_carbs=50)
        assert req.target_servings is None
        assert req.target_min_grams == 200
        assert req.target_max_grams == 300

    def test_with_target_servings(self):
        req = CalcRequest(total_weight_grams=1000, pan_id=1, total_carbs=50, target_servings=4)
        assert req.target_servings == 4

    def test_target_servings_zero_rejected(self):
        with pytest.raises(ValidationError):
            CalcRequest(total_weight_grams=1000, pan_id=1, total_carbs=50, target_servings=0)

    def test_target_servings_negative_rejected(self):
        with pytest.raises(ValidationError):
            CalcRequest(total_weight_grams=1000, pan_id=1, total_carbs=50, target_servings=-1)

    def test_target_servings_none_allowed(self):
        req = CalcRequest(total_weight_grams=1000, pan_id=1, total_carbs=50, target_servings=None)
        assert req.target_servings is None

    def test_zero_weight_rejected(self):
        with pytest.raises(ValidationError):
            CalcRequest(total_weight_grams=0, pan_id=1, total_carbs=50)

    def test_negative_carbs_rejected(self):
        with pytest.raises(ValidationError):
            CalcRequest(total_weight_grams=1000, pan_id=1, total_carbs=-1)

    def test_zero_carbs_allowed(self):
        req = CalcRequest(total_weight_grams=1000, pan_id=1, total_carbs=0)
        assert req.total_carbs == 0

    def test_custom_range(self):
        req = CalcRequest(
            total_weight_grams=1000, pan_id=1, total_carbs=50,
            target_min_grams=100, target_max_grams=150,
        )
        assert req.target_min_grams == 100
        assert req.target_max_grams == 150


class TestCalcResponse:
    def test_valid(self):
        resp = CalcResponse(
            net_weight_grams=800, servings=4, serving_weight_grams=200, carbs_per_serving=12.5,
        )
        assert resp.servings == 4
        assert resp.carbs_per_serving == 12.5
