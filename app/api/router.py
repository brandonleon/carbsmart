from fastapi import APIRouter

from app.api.routes import calc, pans

api_router = APIRouter()
api_router.include_router(pans.router, prefix="/pans", tags=["pans"])
api_router.include_router(calc.router, prefix="/calc", tags=["calc"])
