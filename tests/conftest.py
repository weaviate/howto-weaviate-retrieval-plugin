import subprocess
import pytest
import weaviate
import time
import requests
import server.database

HOST = "http://localhost:8080"


@pytest.fixture(scope="module")
def weaviate_server():
    subprocess.run(["docker-compose", "-f", "tests/docker-compose.yml", "up", "-d"])
    _wait_for_weaviate()
    yield
    subprocess.run(["docker-compose", "-f", "tests/docker-compose.yml", "down"])


@pytest.fixture
def weaviate_client(weaviate_server):
    client = weaviate.Client(HOST)
    client.schema.delete_all()
    client.schema.create_class(server.database.SCHEMA)
    yield client
    client.schema.delete_all()


def _wait_for_weaviate():
    while True:
        try:
            response = requests.get(f"{HOST}/v1/.well-known/ready")
            if response.status_code == 200:
                return
            else:
                time.sleep(0.5)
        except requests.exceptions.ConnectionError:
            time.sleep(1)
