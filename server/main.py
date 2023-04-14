from typing import List
from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager

from .database import get_client, init_db, INDEX_NAME
from .embedding import get_embedding
from pydantic import BaseModel


class Document(BaseModel):
    text: str
    document_id: str


class Query(BaseModel):
    text: str
    limit: int = 5


class QueryResult(BaseModel):
    document: Document
    score: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


def get_weaviate_client():
    """
    Get a client to the Weaviate server
    """
    yield get_client()


@app.get("/")
def read_root():
    """
    Say hello to the world
    """
    return {"Hello": "World"}


@app.post("/upsert")
def upsert(doc: Document, client=Depends(get_weaviate_client)):
    """
    Insert a document into weaviate
    """
    with client.batch as batch:
        batch.add_data_object(
            data_object=doc.dict(),
            class_name=INDEX_NAME,
            vector=get_embedding(doc.text),
        )

    return {"status": "ok"}


@app.post("/query", response_model=List[QueryResult])
def query(query: Query, client=Depends(get_weaviate_client)) -> List[Document]:
    """
    Query weaviate for documents
    """
    query_vector = get_embedding(query.text)

    results = (
        client.query.get(INDEX_NAME, ["document_id", "text"])
        .with_near_vector({"vector": query_vector})
        .with_limit(query.limit)
        .with_additional("certainty")
        .do()
    )

    docs = results["data"]["Get"][INDEX_NAME]

    return [
        QueryResult(
            document={"text": doc["text"], "document_id": doc["document_id"]},
            score=doc["_additional"]["certainty"],
        )
        for doc in docs
    ]
