"""
Tests for restocking API endpoints (recommendations and restock orders).
"""
import pytest

# Cost of restocking every forecast item to its full forecasted demand
FULL_RESTOCK_COST = 65147.48


def growth(item):
    return (item["forecasted_demand"] - item["current_demand"]) / item["current_demand"]


class TestDemandForecastPricing:
    """Test that demand forecasts carry the fields restocking depends on."""

    def test_demand_forecasts_have_cost_and_lead_time(self, client):
        """Test that every forecast has a unit cost and lead time."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        for forecast in response.json():
            assert isinstance(forecast["unit_cost"], (int, float))
            assert isinstance(forecast["lead_time_days"], int)
            assert forecast["unit_cost"] > 0
            assert 7 <= forecast["lead_time_days"] <= 14


class TestRestockRecommendations:
    """Test suite for the restock recommendations endpoint."""

    def test_get_recommendations_structure(self, client):
        """Test the response structure for a typical budget."""
        response = client.get("/api/restock/recommendations?budget=25000")
        assert response.status_code == 200

        data = response.json()
        assert data["budget"] == 25000
        assert "total_cost" in data
        assert "remaining_budget" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0

        for item in data["items"]:
            for field in ["item_sku", "item_name", "trend", "unit_cost",
                          "lead_time_days", "recommended_quantity", "line_total"]:
                assert field in item
            assert item["recommended_quantity"] > 0

    def test_recommendations_zero_budget(self, client):
        """Test that a zero budget recommends nothing."""
        response = client.get("/api/restock/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["items"] == []
        assert data["total_cost"] == 0

    def test_recommendations_negative_budget(self, client):
        """Test that a negative budget is rejected."""
        response = client.get("/api/restock/recommendations?budget=-100")
        assert response.status_code == 422

    def test_recommendations_missing_budget(self, client):
        """Test that the budget parameter is required."""
        response = client.get("/api/restock/recommendations")
        assert response.status_code == 422

    def test_recommendations_large_budget_covers_everything(self, client):
        """Test that a budget above the full cost restocks every item fully."""
        forecasts = client.get("/api/demand").json()
        response = client.get("/api/restock/recommendations?budget=1000000")
        data = response.json()

        assert len(data["items"]) == len(forecasts)
        for item in data["items"]:
            assert item["recommended_quantity"] == item["forecasted_demand"]
        assert abs(data["total_cost"] - FULL_RESTOCK_COST) < 0.01

    @pytest.mark.parametrize("budget", [500, 7500, 25000, 40000, 65000])
    def test_recommendations_within_budget(self, client, budget):
        """Test that the recommended total never exceeds the budget."""
        data = client.get(f"/api/restock/recommendations?budget={budget}").json()

        line_sum = sum(item["line_total"] for item in data["items"])
        assert abs(data["total_cost"] - line_sum) < 0.01
        assert data["total_cost"] <= budget
        assert abs(data["remaining_budget"] - (budget - data["total_cost"])) < 0.01

    def test_recommendations_sorted_by_growth(self, client):
        """Test that items are ranked by demand growth, highest first."""
        data = client.get("/api/restock/recommendations?budget=1000000").json()
        growths = [growth(item) for item in data["items"]]
        assert growths == sorted(growths, reverse=True)

    def test_recommendations_only_last_item_partial(self, client):
        """Test that only the final recommended item can be partially filled."""
        data = client.get("/api/restock/recommendations?budget=25000").json()
        items = data["items"]

        for item in items[:-1]:
            assert item["recommended_quantity"] == item["forecasted_demand"]
        assert items[-1]["recommended_quantity"] <= items[-1]["forecasted_demand"]

    def test_recommendations_line_total_calculation(self, client):
        """Test that line totals equal quantity times unit cost."""
        data = client.get("/api/restock/recommendations?budget=25000").json()
        for item in data["items"]:
            expected = item["recommended_quantity"] * item["unit_cost"]
            assert abs(item["line_total"] - expected) < 0.01


class TestRestockOrders:
    """Test suite for submitting and listing restock orders."""

    def test_get_restock_orders_empty(self, client):
        """Test that no restock orders exist before any are submitted."""
        response = client.get("/api/restock-orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restock_order(self, client):
        """Test submitting a valid restock order."""
        payload = {
            "budget": 5000,
            "items": [
                {"item_sku": "FLT-405", "quantity": 100},
                {"item_sku": "MTR-304", "quantity": 5},
            ],
        }
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["order_number"] == "RST-0001"
        assert order["status"] == "Submitted"
        assert len(order["items"]) == 2
        # 100 x 9.80 + 5 x 245.00
        assert abs(order["total_value"] - 2205.0) < 0.01
        assert "T" in order["submitted_date"]
        assert "T" in order["expected_delivery"]

    def test_restock_order_lead_time_is_slowest_item(self, client):
        """Test that order lead time equals the longest item lead time."""
        forecasts = {f["item_sku"]: f for f in client.get("/api/demand").json()}
        skus = ["GSK-203", "CTL-330", "WDG-001"]
        payload = {"budget": 100000, "items": [{"item_sku": s, "quantity": 1} for s in skus]}

        order = client.post("/api/restock-orders", json=payload).json()
        assert order["lead_time_days"] == max(forecasts[s]["lead_time_days"] for s in skus)

    def test_restock_order_expected_delivery_calculation(self, client):
        """Test that expected delivery is the submitted date plus lead time."""
        from datetime import datetime, timedelta

        payload = {"budget": 1000, "items": [{"item_sku": "PSU-501", "quantity": 10}]}
        order = client.post("/api/restock-orders", json=payload).json()

        submitted = datetime.fromisoformat(order["submitted_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert expected - submitted == timedelta(days=order["lead_time_days"])

    def test_restock_order_uses_server_prices(self, client):
        """Test that prices come from the server, ignoring any client-sent price."""
        payload = {
            "budget": 1000,
            "items": [{"item_sku": "MTR-304", "quantity": 2, "unit_cost": 0.01}],
        }
        order = client.post("/api/restock-orders", json=payload).json()
        assert order["items"][0]["unit_cost"] == 245.0
        assert abs(order["total_value"] - 490.0) < 0.01

    def test_created_restock_order_appears_in_list(self, client):
        """Test that submitted orders are listed newest first."""
        for qty in (1, 2):
            client.post("/api/restock-orders",
                        json={"budget": 1000, "items": [{"item_sku": "GSK-203", "quantity": qty}]})

        data = client.get("/api/restock-orders").json()
        assert [o["order_number"] for o in data] == ["RST-0002", "RST-0001"]

    def test_restock_order_over_budget(self, client):
        """Test that an order costing more than the budget is rejected."""
        payload = {"budget": 100, "items": [{"item_sku": "MTR-304", "quantity": 1}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400
        assert "exceeds budget" in response.json()["detail"]
        assert client.get("/api/restock-orders").json() == []

    def test_restock_order_unknown_sku(self, client):
        """Test that an unknown SKU is rejected."""
        payload = {"budget": 1000, "items": [{"item_sku": "NOPE-999", "quantity": 1}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400
        assert "unknown sku" in response.json()["detail"].lower()

    def test_restock_order_empty_items(self, client):
        """Test that an order with no items is rejected."""
        response = client.post("/api/restock-orders", json={"budget": 1000, "items": []})
        assert response.status_code == 400

    @pytest.mark.parametrize("quantity", [0, -5])
    def test_restock_order_non_positive_quantity(self, client, quantity):
        """Test that zero or negative quantities are rejected."""
        payload = {"budget": 1000, "items": [{"item_sku": "GSK-203", "quantity": quantity}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400

    def test_restock_order_duplicate_sku(self, client):
        """Test that the same SKU can't appear twice in one order."""
        payload = {
            "budget": 1000,
            "items": [{"item_sku": "GSK-203", "quantity": 1}, {"item_sku": "GSK-203", "quantity": 2}],
        }
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400

    def test_recommendations_can_be_ordered(self, client):
        """Test that a recommendation set submits successfully at the same budget."""
        rec = client.get("/api/restock/recommendations?budget=25000").json()
        payload = {
            "budget": 25000,
            "items": [{"item_sku": i["item_sku"], "quantity": i["recommended_quantity"]}
                      for i in rec["items"]],
        }
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201
        assert abs(response.json()["total_value"] - rec["total_cost"]) < 0.01
