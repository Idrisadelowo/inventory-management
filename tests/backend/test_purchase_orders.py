"""
Tests for purchase order API endpoints.
"""


class TestPurchaseOrderEndpoints:
    """Test suite for purchase-order-related endpoints."""

    def po_payload(self, **overrides):
        payload = {
            "backlog_item_id": "1",
            "supplier_name": "Acme Filters",
            "quantity": 350,
            "unit_cost": 12.5,
            "expected_delivery_date": "2025-11-15",
            "notes": "Rush order",
        }
        payload.update(overrides)
        return payload

    def test_create_purchase_order(self, client):
        """Test creating a purchase order for a backlog item."""
        response = client.post("/api/purchase-orders", json=self.po_payload())
        assert response.status_code == 201

        po = response.json()
        assert po["id"].startswith("PO-")
        assert po["backlog_item_id"] == "1"
        assert po["supplier_name"] == "Acme Filters"
        assert po["quantity"] == 350
        assert po["status"] == "Pending"
        assert "T" in po["created_date"]

    def test_get_purchase_order_by_id(self, client):
        """Test getting a created purchase order by ID."""
        created = client.post("/api/purchase-orders", json=self.po_payload()).json()

        response = client.get(f"/api/purchase-orders/{created['id']}")
        assert response.status_code == 200
        assert response.json() == created

    def test_get_nonexistent_purchase_order(self, client):
        """Test getting a purchase order that doesn't exist."""
        response = client.get("/api/purchase-orders/PO-9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_backlog_links_purchase_order(self, client):
        """Test that the backlog reports the PO ID once one is created."""
        backlog = client.get("/api/backlog").json()
        item = next(b for b in backlog if b["id"] == "1")
        assert item["has_purchase_order"] is False
        assert item["purchase_order_id"] is None

        created = client.post("/api/purchase-orders", json=self.po_payload()).json()

        backlog = client.get("/api/backlog").json()
        item = next(b for b in backlog if b["id"] == "1")
        assert item["has_purchase_order"] is True
        assert item["purchase_order_id"] == created["id"]

    def test_create_purchase_order_unknown_backlog_item(self, client):
        """Test creating a purchase order for a backlog item that doesn't exist."""
        response = client.post(
            "/api/purchase-orders", json=self.po_payload(backlog_item_id="nonexistent-999")
        )
        assert response.status_code == 404

    def test_create_duplicate_purchase_order(self, client):
        """Test that a backlog item can only have one purchase order."""
        client.post("/api/purchase-orders", json=self.po_payload())
        response = client.post("/api/purchase-orders", json=self.po_payload())
        assert response.status_code == 409

    def test_create_purchase_order_invalid_values(self, client):
        """Test that blank supplier, non-positive quantity and negative cost are rejected."""
        for overrides in ({"supplier_name": "  "}, {"quantity": 0}, {"unit_cost": -1}):
            response = client.post("/api/purchase-orders", json=self.po_payload(**overrides))
            assert response.status_code == 400, overrides
