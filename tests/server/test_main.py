from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_weaviate_server(weaviate_client):
    node_status = weaviate_client.cluster.get_nodes_status()[0]
    assert node_status["status"] == "HEALTHY"
