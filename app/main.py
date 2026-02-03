from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.db import init_db
from app.db import get_db
from app.repositories import pans as pans_repo
from app.web.router import web_router

app = FastAPI(title="CarbSmart API")
app.include_router(api_router, prefix="/api")
app.include_router(web_router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root(db: Session = Depends(get_db)) -> RedirectResponse:
    pans = pans_repo.list_pans(db)
    target = "/calc" if pans else "/pans"
    return RedirectResponse(url=target, status_code=303)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
