from typing import List
from fastapi import Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from .database import get_client, init_db, INDEX_NAME
from .embedding import get_embedding
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials


class Document(BaseModel):
    text: str
    document_id: str


class Query(BaseModel):
    text: str
    limit: int = 5


class QueryResult(BaseModel):
    document: Document
    score: float


class DeleteRequest(BaseModel):
    document_id: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

# for localhost deployment
if os.getenv("ENV", "dev") == "dev":
    origins = [
        f"http://localhost:8000",
        "https://chat.openai.com",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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
def upsert(
    doc: Document,
    client=Depends(get_weaviate_client),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
):
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
def query(
    query: Query,
    client=Depends(get_weaviate_client),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
) -> List[Document]:
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


@app.post("/delete")
def delete(
    delete_request: DeleteRequest,
    client=Depends(get_weaviate_client),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
):
    """
    Delete a document from weaviate
    """
    result = client.batch.delete_objects(
        class_name=INDEX_NAME,
        where={
            "operator": "Equal",
            "path": ["document_id"],
            "valueString": delete_request.document_id,
        },
    )

    if result["results"]["successful"] == 1:
        return {"status": "ok"}
    else:
        return {"status": "not found"}
