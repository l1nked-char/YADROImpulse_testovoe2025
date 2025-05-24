import pytest


@pytest.mark.usefixtures("client", "test_graph")
class TestGraphRead:
    def test_read_graph(self, client, test_graph):
        response = client.get(f"/api/graph/{test_graph}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_graph
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1

    def test_read_invalid_graph(self, client):
        response = client.get("/api/graph/999999/")
        assert response.status_code == 404
        assert "message" in response.json()
