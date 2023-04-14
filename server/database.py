import weaviate
import os
import logging

INDEX_NAME = "Document"

SCHEMA = {
    "class": INDEX_NAME,
    "properties": [
        {"name": "text", "dataType": ["text"]},
        {"name": "document_id", "dataType": ["string"]},
    ],
}


def get_client():
    """
    Get a client to the Weaviate server
    """
    host = os.environ.get("WEAVIATE_HOST", "http://localhost:8080")
    return weaviate.Client(host)


def init_db():
    """
    Create the schema for the database if it doesn't exist yet
    """
    client = get_client()

    if not client.schema.contains(SCHEMA):
        logging.debug("Creating schema")
        client.schema.create_class(SCHEMA)
    else:
        class_name = SCHEMA["class"]
        logging.debug(f"Schema for {class_name} already exists")
        logging.debug("Skipping schema creation")
