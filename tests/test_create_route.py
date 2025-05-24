import pytest


class TestGraphCreation:
    @pytest.mark.parametrize("test_data,expected_status", [
        ({
             "nodes": [{"name": "A"}, {"name": "B"}],
             "edges": [{"source": "A", "target": "B"}]
         }, 201),
        ({
             "nodes": [{"invalid_field": "A"}],
             "edges": [{"source": "A", "target": "B"}]
         }, 422)
    ])
    def test_graph_creation(self, client, test_data, expected_status):
        response = client.post("/api/graph/", json=test_data)
        assert response.status_code == expected_status
        if expected_status == 201:
            assert "id" in response.json()
            assert isinstance(response.json()["id"], int)
