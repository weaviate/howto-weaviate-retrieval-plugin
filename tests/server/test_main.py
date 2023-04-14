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


def test_upsert(weaviate_client):
    response = client.post("/upsert", json={"text": "Hello World", "document_id": "1"})
    assert response.status_code == 200

    docs = weaviate_client.data_object.get(with_vector=True)["objects"]
    assert len(docs) == 1
    assert docs[0]["properties"]["text"] == "Hello World"
    assert docs[0]["properties"]["document_id"] == "1"
    assert docs[0]["vector"] is not None
