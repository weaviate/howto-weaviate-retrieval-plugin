from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager

from .database import get_client, init_db, INDEX_NAME
from .embedding import get_embedding
from pydantic import BaseModel


class Document(BaseModel):
    text: str
    document_id: str


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
