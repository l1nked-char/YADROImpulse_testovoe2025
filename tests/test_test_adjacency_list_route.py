import pytest


@pytest.mark.usefixtures("client", "test_graph")
class TestAdjacency:
    def test_adjacency_list(self, client, test_graph):
        response = client.get(f"/api/graph/{test_graph}/adjacency_list")
        assert response.status_code == 200
        adjacency_list = response.json()["adjacency_list"]
        assert adjacency_list["A"] == ["B"]
        assert adjacency_list["B"] == []

    def test_reverse_adjacency_list(self, client, test_graph):
        response = client.get(f"/api/graph/{test_graph}/reverse_adjacency_list")
        assert response.status_code == 200
        reverse_list = response.json()["adjacency_list"]
        assert reverse_list["B"] == ["A"]
        assert reverse_list["A"] == []
