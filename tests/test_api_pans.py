class TestListPans:
    def test_empty(self, client):
        resp = client.get("/api/pans")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_pans(self, client, sample_pan):
        resp = client.get("/api/pans")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Sheet Pan"


class TestCreatePan:
    def test_create(self, client):
        resp = client.post("/api/pans", json={"name": "Skillet", "weight_grams": 1200})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Skillet"
        assert data["weight_grams"] == 1200
        assert "id" in data

    def test_with_capacity(self, client):
        resp = client.post(
            "/api/pans",
            json={"name": "Stock Pot", "weight_grams": 2240, "capacity_label": "6 L"},
        )
        assert resp.status_code == 201
        assert resp.json()["capacity_label"] == "6 L"

    def test_duplicate_rejected(self, client, sample_pan):
        resp = client.post(
            "/api/pans",
            json={"name": "Sheet Pan", "weight_grams": 600, "capacity_label": "Half"},
        )
        assert resp.status_code == 409

    def test_missing_name(self, client):
        resp = client.post("/api/pans", json={"weight_grams": 500})
        assert resp.status_code == 422

    def test_missing_weight(self, client):
        resp = client.post("/api/pans", json={"name": "Pan"})
        assert resp.status_code == 422


class TestUpdatePan:
    def test_update_name(self, client, sample_pan):
        resp = client.put(f"/api/pans/{sample_pan.id}", json={"name": "Renamed"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    def test_update_weight(self, client, sample_pan):
        resp = client.put(f"/api/pans/{sample_pan.id}", json={"weight_grams": 999})
        assert resp.status_code == 200
        assert resp.json()["weight_grams"] == 999

    def test_not_found(self, client):
        resp = client.put("/api/pans/9999", json={"name": "X"})
        assert resp.status_code == 404


class TestDeletePan:
    def test_delete(self, client, sample_pan):
        resp = client.delete(f"/api/pans/{sample_pan.id}")
        assert resp.status_code == 204

        resp = client.get("/api/pans")
        assert resp.json() == []

    def test_not_found(self, client):
        resp = client.delete("/api/pans/9999")
        assert resp.status_code == 404
