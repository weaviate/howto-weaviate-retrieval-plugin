from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import get_client, init_db

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
