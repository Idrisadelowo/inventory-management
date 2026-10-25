"""
Tests for task API endpoints.
"""


class TestTasksEndpoints:
    """Test suite for task-related endpoints."""

    def create_task(self, client, **overrides):
        payload = {"title": "Check Q4 stock", "priority": "high", "dueDate": "2025-12-01"}
        payload.update(overrides)
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 201
        return response.json()

    def test_get_all_tasks_empty(self, client):
        """Test that no tasks exist before any are created."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_task(self, client):
        """Test creating a task returns it as pending with a prefixed ID."""
        task = self.create_task(client)
        assert task["id"].startswith("task-")
        assert task["title"] == "Check Q4 stock"
        assert task["priority"] == "high"
        assert task["dueDate"] == "2025-12-01"
        assert task["status"] == "pending"

    def test_get_tasks_newest_first(self, client):
        """Test that created tasks are listed newest first."""
        first = self.create_task(client, title="First")
        second = self.create_task(client, title="Second")

        data = client.get("/api/tasks").json()
        assert [t["id"] for t in data] == [second["id"], first["id"]]

    def test_create_task_blank_title(self, client):
        """Test that a whitespace-only title is rejected."""
        response = client.post("/api/tasks", json={"title": "   ", "dueDate": "2025-12-01"})
        assert response.status_code == 400

    def test_create_task_invalid_priority(self, client):
        """Test that an unknown priority is rejected."""
        response = client.post(
            "/api/tasks", json={"title": "x", "priority": "urgent", "dueDate": "2025-12-01"}
        )
        assert response.status_code == 422

    def test_toggle_task(self, client):
        """Test toggling a task flips between pending and completed."""
        task = self.create_task(client)

        response = client.patch(f"/api/tasks/{task['id']}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

        response = client.patch(f"/api/tasks/{task['id']}")
        assert response.json()["status"] == "pending"

    def test_delete_task(self, client):
        """Test deleting a task removes it from the list."""
        task = self.create_task(client)

        response = client.delete(f"/api/tasks/{task['id']}")
        assert response.status_code == 200
        assert client.get("/api/tasks").json() == []

    def test_delete_task_ids_not_reused(self, client):
        """Test that deleting a task doesn't cause its ID to collide with a newer task."""
        first = self.create_task(client, title="First")
        second = self.create_task(client, title="Second")
        client.delete(f"/api/tasks/{first['id']}")

        third = self.create_task(client, title="Third")
        assert third["id"] != second["id"]

    def test_toggle_nonexistent_task(self, client):
        """Test toggling a task that doesn't exist."""
        response = client.patch("/api/tasks/task-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist."""
        response = client.delete("/api/tasks/task-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
