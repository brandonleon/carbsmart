from fastapi import FastAPI

from app.api.router import api_router
from app.db import init_db
from app.web.router import web_router

app = FastAPI(title="CarbSmart API")
app.include_router(api_router, prefix="/api")
app.include_router(web_router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
