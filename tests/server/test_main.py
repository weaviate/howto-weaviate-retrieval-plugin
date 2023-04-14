from fastapi.testclient import TestClient
from server.main import app
import pytest

client = TestClient(app)


@pytest.fixture
def documents(weaviate_client):
    docs = [
        {"text": "The lion is the king of the jungle", "document_id": "1"},
        {"text": "The lion is a carnivore", "document_id": "2"},
        {"text": "The lion is a large animal", "document_id": "3"},
        {"text": "The capital of France is Paris", "document_id": "4"},
        {"text": "The capital of Germany is Berlin", "document_id": "5"},
    ]

    for doc in docs:
        client.post("/upsert", json=doc)


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


def test_query(documents):
    LIMIT = 3
    response = client.post("/query", json={"text": "lion", "limit": LIMIT})

    results = response.json()

    assert len(results) == LIMIT
    for result in results:
        assert "lion" in result["document"]["text"]


def test_delete(documents, weaviate_client):
    num_docs_before_delete = weaviate_client.data_object.get()["totalResults"]

    response = client.post("/delete", json={"document_id": "3"})
    assert response.status_code == 200

    num_docs_after_delete = weaviate_client.data_object.get()["totalResults"]

    assert num_docs_after_delete == num_docs_before_delete - 1
