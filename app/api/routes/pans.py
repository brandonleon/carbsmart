from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Pan, PanCreate, PanUpdate
from app.repositories import pans as pans_repo

router = APIRouter()


@router.get("", response_model=list[Pan])
def list_pans(db: Session = Depends(get_db)) -> list[Pan]:
    return pans_repo.list_pans(db)


@router.post("", response_model=Pan, status_code=201)
def create_pan(payload: PanCreate, db: Session = Depends(get_db)) -> Pan:
    try:
        return pans_repo.create_pan(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Pan name and capacity already exists",
        ) from exc


@router.put("/{pan_id}", response_model=Pan)
def update_pan(pan_id: int, payload: PanUpdate, db: Session = Depends(get_db)) -> Pan:
    pan = pans_repo.get_pan(db, pan_id)
    if not pan:
        raise HTTPException(status_code=404, detail="Pan not found")
    try:
        return pans_repo.update_pan(db, pan, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Pan name and capacity already exists",
        ) from exc


@router.delete("/{pan_id}", status_code=204)
def delete_pan(pan_id: int, db: Session = Depends(get_db)) -> None:
    pan = pans_repo.get_pan(db, pan_id)
    if not pan:
        raise HTTPException(status_code=404, detail="Pan not found")
    pans_repo.delete_pan(db, pan)
    return None
