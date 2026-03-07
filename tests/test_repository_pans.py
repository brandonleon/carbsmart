from app.models import PanCreate, PanUpdate
from app.repositories import pans as pans_repo


class TestListPans:
    def test_empty(self, db):
        assert pans_repo.list_pans(db) == []

    def test_returns_all(self, db, sample_pan):
        result = pans_repo.list_pans(db)
        assert len(result) == 1
        assert result[0].id == sample_pan.id

    def test_ordered_by_name(self, db):
        pans_repo.create_pan(db, PanCreate(name="Zebra Pan", weight_grams=100))
        pans_repo.create_pan(db, PanCreate(name="Alpha Pan", weight_grams=200))
        result = pans_repo.list_pans(db)
        assert result[0].name == "Alpha Pan"
        assert result[1].name == "Zebra Pan"


class TestGetPan:
    def test_exists(self, db, sample_pan):
        pan = pans_repo.get_pan(db, sample_pan.id)
        assert pan is not None
        assert pan.name == "Sheet Pan"

    def test_not_found(self, db):
        assert pans_repo.get_pan(db, 9999) is None


class TestCreatePan:
    def test_create(self, db):
        pan = pans_repo.create_pan(db, PanCreate(name="Skillet", weight_grams=1200))
        assert pan.id is not None
        assert pan.name == "Skillet"
        assert pan.weight_grams == 1200
        assert pan.capacity_label == ""

    def test_with_capacity(self, db):
        pan = pans_repo.create_pan(
            db, PanCreate(name="Pot", weight_grams=2000, capacity_label="8 qt"),
        )
        assert pan.capacity_label == "8 qt"

    def test_with_notes(self, db):
        pan = pans_repo.create_pan(
            db, PanCreate(name="Cast Iron", weight_grams=3000, notes="Heavy"),
        )
        assert pan.notes == "Heavy"

    def test_null_capacity_becomes_empty(self, db):
        pan = pans_repo.create_pan(
            db, PanCreate(name="Simple", weight_grams=500, capacity_label=None),
        )
        assert pan.capacity_label == ""


class TestUpdatePan:
    def test_update_name(self, db, sample_pan):
        updated = pans_repo.update_pan(db, sample_pan, PanUpdate(name="Renamed"))
        assert updated.name == "Renamed"
        assert updated.weight_grams == 500  # unchanged

    def test_update_weight(self, db, sample_pan):
        updated = pans_repo.update_pan(db, sample_pan, PanUpdate(weight_grams=999))
        assert updated.weight_grams == 999

    def test_update_capacity_to_none_becomes_empty(self, db, sample_pan):
        updated = pans_repo.update_pan(db, sample_pan, PanUpdate(capacity_label=None))
        assert updated.capacity_label == ""

    def test_no_op_update(self, db, sample_pan):
        updated = pans_repo.update_pan(db, sample_pan, PanUpdate())
        assert updated.name == "Sheet Pan"


class TestDeletePan:
    def test_delete(self, db, sample_pan):
        pans_repo.delete_pan(db, sample_pan)
        assert pans_repo.get_pan(db, sample_pan.id) is None

    def test_list_empty_after_delete(self, db, sample_pan):
        pans_repo.delete_pan(db, sample_pan)
        assert pans_repo.list_pans(db) == []
