from html import escape
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories import pans as pans_repo
from app.services.calc import calculate_plan
from app.web.templates import templates

router = APIRouter()


def _pan_label(pan) -> str:
    label = pan.name
    if pan.capacity_label:
        label = f"{label} ({pan.capacity_label})"
    label = f"{label} - {pan.weight_grams:.0f} g"
    return label


def _build_share_url(form: dict[str, str], mini: bool = True) -> str:
    params = {k: v for k, v in form.items() if v}
    if mini:
        params["view"] = "mini"
    return f"/calc?{urlencode(params)}"


def _pan_options(pans):
    return [{"id": pan.id, "label": _pan_label(pan)} for pan in pans]


@router.get("/calc", response_class=HTMLResponse)
def calc_page(
    request: Request,
    pan_id: int | None = Query(default=None),
    total_weight_grams: float | None = Query(default=None),
    total_carbs: float | None = Query(default=None),
    target_servings: int | None = Query(default=None),
    target_min_grams: float | None = Query(default=None),
    target_max_grams: float | None = Query(default=None),
    view: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    pans = pans_repo.list_pans(db)

    has_params = pan_id is not None and total_weight_grams is not None and total_carbs is not None
    if not has_params:
        return templates.TemplateResponse(
            request,
            "calc/page.html",
            {"pans": _pan_options(pans), "form": {}, "result": None, "error": None, "share_url": None, "active_nav": "calc"},
        )

    pan = pans_repo.get_pan(db, pan_id)
    if not pan:
        return templates.TemplateResponse(
            request,
            "calc/page.html",
            {"pans": _pan_options(pans), "form": {}, "result": None, "error": "Pan not found", "share_url": None, "active_nav": "calc"},
            status_code=404,
        )

    eff_min = target_min_grams if target_min_grams is not None else 200.0
    eff_max = target_max_grams if target_max_grams is not None else 300.0

    form_values = {
        "pan_id": str(pan_id),
        "total_weight_grams": f"{total_weight_grams}",
        "total_carbs": f"{total_carbs}",
        "target_servings": f"{target_servings}" if target_servings is not None else "",
        "target_min_grams": f"{eff_min}",
        "target_max_grams": f"{eff_max}",
    }

    if target_servings is None and eff_min > eff_max:
        return templates.TemplateResponse(
            request,
            "calc/page.html",
            {"pans": _pan_options(pans), "form": form_values, "result": None, "error": "Target min must be <= target max", "share_url": None, "active_nav": "calc"},
            status_code=422,
        )

    try:
        net_weight, servings, serving_weight, carbs_per_serving = calculate_plan(
            total_weight_grams,
            pan.weight_grams,
            total_carbs,
            eff_min,
            eff_max,
            target_servings,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "calc/page.html",
            {"pans": _pan_options(pans), "form": form_values, "result": None, "error": str(exc), "share_url": None, "active_nav": "calc"},
            status_code=422,
        )

    result = {
        "net_weight_grams": f"{net_weight:.1f}",
        "servings": f"{servings}",
        "serving_weight_grams": f"{serving_weight:.1f}",
        "carbs_per_serving": f"{carbs_per_serving:.1f}",
    }

    mini_url = _build_share_url(form_values, mini=True)
    full_url = _build_share_url(form_values, mini=False)

    if view == "mini":
        return templates.TemplateResponse(
            request,
            "calc/mini.html",
            {"result": result, "full_url": full_url, "mini_url": mini_url, "active_nav": "calc"},
        )

    return templates.TemplateResponse(
        request,
        "calc/page.html",
        {"pans": _pan_options(pans), "form": form_values, "result": result, "share_url": mini_url, "active_nav": "calc"},
    )


@router.post("/calc", response_class=HTMLResponse)
def calc_submit(
    request: Request,
    pan_id: int = Form(...),
    total_weight_grams: float = Form(...),
    total_carbs: float = Form(...),
    target_servings: int | None = Form(default=None),
    target_min_grams: float = Form(200),
    target_max_grams: float = Form(300),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    pans = pans_repo.list_pans(db)
    pan = pans_repo.get_pan(db, pan_id)
    if not pan:
        raise HTTPException(status_code=404, detail="Pan not found")

    form_values = {
        "pan_id": str(pan_id),
        "total_weight_grams": f"{total_weight_grams}",
        "total_carbs": f"{total_carbs}",
        "target_servings": f"{target_servings}" if target_servings is not None else "",
        "target_min_grams": f"{target_min_grams}",
        "target_max_grams": f"{target_max_grams}",
    }

    if target_servings is None and target_min_grams > target_max_grams:
        return templates.TemplateResponse(
            request,
            "calc/page.html",
            {"pans": _pan_options(pans), "form": form_values, "result": None, "error": "Target min must be <= target max", "share_url": None, "active_nav": "calc"},
            status_code=422,
        )

    try:
        net_weight, servings, serving_weight, carbs_per_serving = calculate_plan(
            total_weight_grams,
            pan.weight_grams,
            total_carbs,
            target_min_grams,
            target_max_grams,
            target_servings,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "calc/page.html",
            {"pans": _pan_options(pans), "form": form_values, "result": None, "error": str(exc), "share_url": None, "active_nav": "calc"},
            status_code=422,
        )

    result = {
        "net_weight_grams": f"{net_weight:.1f}",
        "servings": f"{servings}",
        "serving_weight_grams": f"{serving_weight:.1f}",
        "carbs_per_serving": f"{carbs_per_serving:.1f}",
    }

    share_url = _build_share_url(form_values, mini=True)
    return templates.TemplateResponse(
        request,
        "calc/page.html",
        {"pans": _pan_options(pans), "form": form_values, "result": result, "share_url": share_url, "active_nav": "calc"},
    )
