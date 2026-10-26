from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from repository_indexer import RepositoryIndexer
from search_engine import SearchEngine


class IndexRequest(BaseModel):
    repository_path: str


app = FastAPI()


@app.get("/search")
def search(query: str, repository_path: str):
    search_engine = SearchEngine()

    try:
        return search_engine.search(query, repository_path)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post("/index")
def index(request: IndexRequest):
    repository_indexer = RepositoryIndexer()

    try:
        repository_indexer.index_repository(request.repository_path)

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except NotADirectoryError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return {"message": "Repository indexed"}