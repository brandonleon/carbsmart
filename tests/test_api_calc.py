class TestCalcAPI:
    def test_basic_calculation(self, client, sample_pan):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 100,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["net_weight_grams"] == 1000.0
        assert data["servings"] == 4
        assert data["serving_weight_grams"] == 250.0
        assert data["carbs_per_serving"] == 25.0

    def test_custom_range(self, client, sample_pan):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 100,
            "target_min_grams": 100,
            "target_max_grams": 150,
        })
        assert resp.status_code == 200
        data = resp.json()
        # 1000g / range 100-150: midpoint 125, 8 servings = 125g
        assert data["servings"] == 8

    def test_with_target_servings(self, client, sample_pan):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 100,
            "target_servings": 2,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["servings"] == 2
        assert data["serving_weight_grams"] == 500.0
        assert data["carbs_per_serving"] == 50.0

    def test_target_servings_overrides_range(self, client, sample_pan):
        # Even with a range that would give 4, target_servings=2 wins
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 100,
            "target_servings": 2,
            "target_min_grams": 200,
            "target_max_grams": 300,
        })
        assert resp.status_code == 200
        assert resp.json()["servings"] == 2

    def test_target_servings_skips_range_validation(self, client, sample_pan):
        # min > max would normally fail, but target_servings bypasses range
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 100,
            "target_servings": 4,
            "target_min_grams": 500,
            "target_max_grams": 100,
        })
        assert resp.status_code == 200
        assert resp.json()["servings"] == 4

    def test_pan_not_found(self, client):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": 9999,
            "total_carbs": 100,
        })
        assert resp.status_code == 404

    def test_min_greater_than_max_rejected(self, client, sample_pan):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 100,
            "target_min_grams": 500,
            "target_max_grams": 100,
        })
        assert resp.status_code == 422

    def test_weight_less_than_pan(self, client, sample_pan):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 100,
            "pan_id": sample_pan.id,
            "total_carbs": 50,
        })
        assert resp.status_code == 422

    def test_zero_carbs(self, client, sample_pan):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 0,
        })
        assert resp.status_code == 200
        assert resp.json()["carbs_per_serving"] == 0.0

    def test_target_servings_zero_rejected(self, client, sample_pan):
        resp = client.post("/api/calc", json={
            "total_weight_grams": 1500,
            "pan_id": sample_pan.id,
            "total_carbs": 100,
            "target_servings": 0,
        })
        assert resp.status_code == 422
