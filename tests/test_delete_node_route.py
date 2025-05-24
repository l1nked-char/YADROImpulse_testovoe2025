import pytest


@pytest.mark.usefixtures("client", "test_graph")
class TestDeleteNode:
    def test_delete_node(self, client, test_graph):
        response = client.delete(f"/api/graph/{test_graph}/node/A")
        assert response.status_code == 204

        get_response = client.get(f"/api/graph/{test_graph}/")
        assert "A" not in [node["name"] for node in get_response.json()["nodes"]]

        response = client.delete(f"/api/graph/{test_graph}/node/INVALID")
        assert response.status_code == 404
