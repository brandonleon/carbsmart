class TestCalcPage:
    def test_get_page(self, client):
        resp = client.get("/calc")
        assert resp.status_code == 200
        assert "Serving Calculator" in resp.text

    def test_shows_pans_in_dropdown(self, client, sample_pan):
        resp = client.get("/calc")
        assert resp.status_code == 200
        assert "Sheet Pan" in resp.text

    def test_empty_state_when_no_pans(self, client):
        resp = client.get("/calc")
        assert "Add a pan first" in resp.text


class TestCalcSubmit:
    def test_basic_submission(self, client, sample_pan):
        resp = client.post("/calc", data={
            "pan_id": sample_pan.id,
            "total_weight_grams": 1500,
            "total_carbs": 100,
            "target_min_grams": 200,
            "target_max_grams": 300,
        })
        assert resp.status_code == 200
        assert "Results" in resp.text
        assert "1000.0" in resp.text  # net weight
        assert "250.0" in resp.text   # serving weight

    def test_with_target_servings(self, client, sample_pan):
        resp = client.post("/calc", data={
            "pan_id": sample_pan.id,
            "total_weight_grams": 1500,
            "total_carbs": 100,
            "target_servings": 2,
            "target_min_grams": 200,
            "target_max_grams": 300,
        })
        assert resp.status_code == 200
        assert "500.0" in resp.text   # 1000g / 2 servings

    def test_target_servings_empty_string_treated_as_none(self, client, sample_pan):
        resp = client.post("/calc", data={
            "pan_id": sample_pan.id,
            "total_weight_grams": 1500,
            "total_carbs": 100,
            "target_servings": "",
            "target_min_grams": 200,
            "target_max_grams": 300,
        })
        assert resp.status_code == 200
        # Falls back to range-based: 4 servings @ 250g
        assert "250.0" in resp.text

    def test_min_greater_than_max_error(self, client, sample_pan):
        resp = client.post("/calc", data={
            "pan_id": sample_pan.id,
            "total_weight_grams": 1500,
            "total_carbs": 100,
            "target_min_grams": 500,
            "target_max_grams": 100,
        })
        assert resp.status_code == 422
        assert "min must be" in resp.text.lower()

    def test_weight_less_than_pan_error(self, client, sample_pan):
        resp = client.post("/calc", data={
            "pan_id": sample_pan.id,
            "total_weight_grams": 100,
            "total_carbs": 50,
            "target_min_grams": 200,
            "target_max_grams": 300,
        })
        assert resp.status_code == 422
        assert "greater than pan weight" in resp.text.lower()

    def test_form_values_persist(self, client, sample_pan):
        resp = client.post("/calc", data={
            "pan_id": sample_pan.id,
            "total_weight_grams": 1234,
            "total_carbs": 56,
            "target_servings": 3,
            "target_min_grams": 200,
            "target_max_grams": 300,
        })
        assert resp.status_code == 200
        assert "1234" in resp.text
        assert "56" in resp.text

    def test_post_results_include_share_link(self, client, sample_pan):
        resp = client.post("/calc", data={
            "pan_id": sample_pan.id,
            "total_weight_grams": 1500,
            "total_carbs": 100,
            "target_servings": 4,
            "target_min_grams": 200,
            "target_max_grams": 300,
        })
        assert resp.status_code == 200
        assert "copyShareLink" in resp.text
        assert "view=mini" in resp.text


class TestCalcShareableUrl:
    def test_get_with_query_params_auto_calculates(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100&target_servings=4"
        )
        assert resp.status_code == 200
        assert "Results" in resp.text
        assert "Ready" in resp.text
        assert "250.0" in resp.text  # 1000g net / 4 servings

    def test_get_with_query_params_prefills_form(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100"
        )
        assert resp.status_code == 200
        assert 'value="1500' in resp.text
        assert 'value="100' in resp.text

    def test_get_with_query_params_shows_share_link(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100&target_servings=4"
        )
        assert resp.status_code == 200
        assert "copyShareLink" in resp.text
        assert "view=mini" in resp.text

    def test_mini_view_shows_only_results(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100"
            f"&target_servings=4&view=mini"
        )
        assert resp.status_code == 200
        assert "Results" in resp.text
        assert "250.0" in resp.text
        # Mini view should NOT have the form or nav
        assert "calcForm" not in resp.text
        assert "Pan Library" not in resp.text

    def test_mini_view_has_edit_values_link(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100"
            f"&target_servings=4&view=mini"
        )
        assert resp.status_code == 200
        assert "Edit values" in resp.text
        # The edit link should NOT contain view=mini
        edit_link_area = resp.text.split("Edit values")[0].rsplit("href=", 1)[1]
        assert "view=mini" not in edit_link_area

    def test_mini_view_has_copy_link_button(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100"
            f"&target_servings=4&view=mini"
        )
        assert resp.status_code == 200
        assert "Copy this link" in resp.text

    def test_get_with_invalid_pan_shows_error(self, client, sample_pan):
        resp = client.get("/calc?pan_id=9999&total_weight_grams=1500&total_carbs=100")
        assert resp.status_code == 404
        assert "not found" in resp.text.lower()

    def test_get_with_weight_less_than_pan(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=100&total_carbs=50"
        )
        assert resp.status_code == 422
        assert "greater than pan weight" in resp.text.lower()

    def test_get_without_params_shows_empty_form(self, client, sample_pan):
        resp = client.get("/calc")
        assert resp.status_code == 200
        assert "How it works" in resp.text

    def test_mini_view_with_range_based_servings(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100"
            f"&target_min_grams=200&target_max_grams=300&view=mini"
        )
        assert resp.status_code == 200
        assert "Results" in resp.text
        assert "250.0" in resp.text  # 1000g net, 4 servings at 250g

    def test_get_uses_default_range_when_omitted(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=1500&total_carbs=100"
        )
        assert resp.status_code == 200
        # Default 200-300 range -> 4 servings @ 250g
        assert "250.0" in resp.text

    def test_mini_view_error_falls_back_to_full_page(self, client, sample_pan):
        resp = client.get(
            f"/calc?pan_id={sample_pan.id}&total_weight_grams=100&total_carbs=50&view=mini"
        )
        # Should show error on full page, not crash on mini view
        assert "greater than pan weight" in resp.text.lower()
