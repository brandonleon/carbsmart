from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PanCreate, PanUpdate
from app.repositories import pans as pans_repo
from app.web.templates import templates

router = APIRouter()


@router.get("/pans", response_class=HTMLResponse)
def pans_page(
    request: Request,
    created: int | None = None,
    updated: int | None = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    pans = pans_repo.list_pans(db)
    return templates.TemplateResponse(
        request,
        "pans/list.html",
        {"pans": pans, "created": bool(created), "updated": bool(updated), "error": None, "active_nav": "pans"},
    )


@router.post("/pans")
def create_pan(
    request: Request,
    name: str = Form(...),
    weight_grams: float = Form(...),
    capacity_label: str | None = Form(default=None),
    notes: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    payload = PanCreate(
        name=name,
        weight_grams=weight_grams,
        capacity_label=capacity_label or None,
        notes=notes or None,
    )
    try:
        pans_repo.create_pan(db, payload)
    except IntegrityError:
        db.rollback()
        pans = pans_repo.list_pans(db)
        return templates.TemplateResponse(
            request,
            "pans/list.html",
            {"pans": pans, "created": False, "updated": False, "error": "Pan name + capacity already exists", "active_nav": "pans"},
            status_code=409,
        )

    return RedirectResponse(url="/pans?created=1", status_code=303)


@router.get("/pans/{pan_id}/edit", response_class=HTMLResponse)
def edit_pan_page(request: Request, pan_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    pan = pans_repo.get_pan(db, pan_id)
    if not pan:
        raise HTTPException(status_code=404, detail="Pan not found")

    return templates.TemplateResponse(
        request,
        "pans/edit.html",
        {"pan": pan, "active_nav": "pans"},
    )


@router.post("/pans/{pan_id}")
def update_pan(
    request: Request,
    pan_id: int,
    name: str = Form(...),
    weight_grams: float = Form(...),
    capacity_label: str | None = Form(default=None),
    notes: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    pan = pans_repo.get_pan(db, pan_id)
    if not pan:
        raise HTTPException(status_code=404, detail="Pan not found")

    payload = PanUpdate(
        name=name,
        weight_grams=weight_grams,
        capacity_label=capacity_label or None,
        notes=notes or None,
    )
    try:
        pans_repo.update_pan(db, pan, payload)
    except IntegrityError:
        db.rollback()
        pans = pans_repo.list_pans(db)
        return templates.TemplateResponse(
            request,
            "pans/list.html",
            {"pans": pans, "created": False, "updated": False, "error": "Pan name + capacity already exists", "active_nav": "pans"},
            status_code=409,
        )

    return RedirectResponse(url="/pans?updated=1", status_code=303)
