from fastapi import APIRouter

from app.web.routes import calc, pans

web_router = APIRouter()
web_router.include_router(pans.router)
web_router.include_router(calc.router)
