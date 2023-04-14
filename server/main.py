from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """
    Say hello to the world
    """
    return {"Hello": "World"}
