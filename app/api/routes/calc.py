from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CalcRequest, CalcResponse
from app.repositories import pans as pans_repo
from app.services.calc import calculate_plan

router = APIRouter()


@router.post("", response_model=CalcResponse)
def calculate(payload: CalcRequest, db: Session = Depends(get_db)) -> CalcResponse:
    pan = pans_repo.get_pan(db, payload.pan_id)
    if not pan:
        raise HTTPException(status_code=404, detail="Pan not found")

    if payload.target_min_grams > payload.target_max_grams:
        raise HTTPException(status_code=422, detail="target_min_grams must be <= target_max_grams")

    try:
        net_weight, servings, serving_weight, carbs_per_serving = calculate_plan(
            payload.total_weight_grams,
            pan.weight_grams,
            payload.total_carbs,
            payload.target_min_grams,
            payload.target_max_grams,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return CalcResponse(
        net_weight_grams=net_weight,
        servings=servings,
        serving_weight_grams=serving_weight,
        carbs_per_serving=carbs_per_serving,
    )
