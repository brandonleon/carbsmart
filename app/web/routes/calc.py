from html import escape

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories import pans as pans_repo
from app.services.calc import calculate_plan

router = APIRouter()


def _pan_label(pan) -> str:
    label = pan.name
    if pan.capacity_label:
        label = f"{label} ({pan.capacity_label})"
    label = f"{label} - {pan.weight_grams:.0f} g"
    return escape(label)


def _render_page(
    pans,
    form: dict[str, str] | None = None,
    result: dict[str, str] | None = None,
    error: str | None = None,
) -> str:
    form = form or {}
    selected_pan = form.get("pan_id", "")

    options = []
    for pan in pans:
        selected = " selected" if str(pan.id) == selected_pan else ""
        options.append(f"<option value=\"{pan.id}\"{selected}>{_pan_label(pan)}</option>")

    options_html = "\n".join(options) if options else "<option value=\"\">No pans available</option>"

    status_html = ""
    if error:
        status_html = f"<p class=\"error\">{escape(error)}</p>"

    result_html = ""
    if result:
        result_html = f"""
        <div class=\"result-card\">
          <h2>Results</h2>
          <dl>
            <div><dt>Net cooked weight</dt><dd>{result['net_weight_grams']} g</dd></div>
            <div><dt>Servings</dt><dd>{result['servings']}</dd></div>
            <div><dt>Serving weight</dt><dd>{result['serving_weight_grams']} g</dd></div>
            <div><dt>Carbs per serving</dt><dd>{result['carbs_per_serving']} g</dd></div>
          </dl>
        </div>
        """

    empty_state = ""
    if not pans:
        empty_state = (
            "<p class=\"notice\">Add a pan first to enable calculations. "
            "<a href=\"/pans\">Go to pan library</a>.</p>"
        )

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>CarbSmart - Serving Calculator</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: "Georgia", "Times New Roman", serif;
        background: #f6efe7;
      }}
      body {{
        margin: 0;
        padding: 2.5rem;
        color: #2a1c12;
        background: radial-gradient(circle at 20% 20%, #fff7ee, #f6efe7 45%, #efe3d6 100%);
      }}
      nav {{
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
      }}
      nav a {{
        text-decoration: none;
        color: #6a3c1d;
        font-weight: 600;
      }}
      h1 {{
        margin-bottom: 0.25rem;
        font-size: 2.25rem;
      }}
      form {{
        display: grid;
        gap: 0.75rem;
        max-width: 28rem;
        padding: 1.25rem;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
      }}
      label {{
        display: flex;
        flex-direction: column;
        font-size: 0.95rem;
        gap: 0.35rem;
      }}
      input, select {{
        padding: 0.5rem 0.6rem;
        border-radius: 6px;
        border: 1px solid #ccb8a5;
        font-size: 1rem;
        background: #fffaf6;
      }}
      button {{
        align-self: start;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        border: none;
        background: #6a3c1d;
        color: #fffaf3;
        font-weight: 600;
        cursor: pointer;
      }}
      .layout {{
        display: grid;
        gap: 2rem;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      }}
      .result-card {{
        padding: 1.5rem;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
      }}
      .result-card dl {{
        display: grid;
        gap: 0.75rem;
        margin: 0;
      }}
      .result-card dt {{
        font-weight: 600;
      }}
      .result-card dd {{
        margin: 0.15rem 0 0;
        font-size: 1.05rem;
      }}
      .notice {{
        color: #1b6b2a;
        font-weight: 600;
      }}
      .error {{
        color: #b3261e;
        font-weight: 600;
      }}
      @media (max-width: 900px) {{
        .layout {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <nav>
      <a href=\"/pans\">Pan Library</a>
      <a href=\"/calc\">Serving Calculator</a>
    </nav>
    <h1>Serving Calculator</h1>
    <p>Enter the total cooked weight with the pan and get precise serving sizes.</p>
    {status_html}
    {empty_state}
    <section class=\"layout\">
      <form method=\"post\" action=\"/calc\">
        <label>
          Pan
          <select name=\"pan_id\" required>
            {options_html}
          </select>
        </label>
        <label>
          Total weight (pan + food) in grams
          <input name=\"total_weight_grams\" type=\"number\" min=\"0\" step=\"0.1\" value=\"{escape(form.get('total_weight_grams', ''))}\" required />
        </label>
        <label>
          Total carbs (grams)
          <input name=\"total_carbs\" type=\"number\" min=\"0\" step=\"0.1\" value=\"{escape(form.get('total_carbs', ''))}\" required />
        </label>
        <label>
          Target serving min (grams)
          <input name=\"target_min_grams\" type=\"number\" min=\"0\" step=\"1\" value=\"{escape(form.get('target_min_grams', '200'))}\" required />
        </label>
        <label>
          Target serving max (grams)
          <input name=\"target_max_grams\" type=\"number\" min=\"0\" step=\"1\" value=\"{escape(form.get('target_max_grams', '300'))}\" required />
        </label>
        <button type=\"submit\">Calculate servings</button>
      </form>
      {result_html}
    </section>
  </body>
</html>"""


@router.get("/calc", response_class=HTMLResponse)
def calc_page(db: Session = Depends(get_db)) -> HTMLResponse:
    pans = pans_repo.list_pans(db)
    return HTMLResponse(_render_page(pans))


@router.post("/calc", response_class=HTMLResponse)
def calc_submit(
    pan_id: int = Form(...),
    total_weight_grams: float = Form(...),
    total_carbs: float = Form(...),
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
        "target_min_grams": f"{target_min_grams}",
        "target_max_grams": f"{target_max_grams}",
    }

    if target_min_grams > target_max_grams:
        return HTMLResponse(
            _render_page(pans, form=form_values, error="Target min must be <= target max"),
            status_code=422,
        )

    try:
        net_weight, servings, serving_weight, carbs_per_serving = calculate_plan(
            total_weight_grams,
            pan.weight_grams,
            total_carbs,
            target_min_grams,
            target_max_grams,
        )
    except ValueError as exc:
        return HTMLResponse(_render_page(pans, form=form_values, error=str(exc)), status_code=422)

    result = {
        "net_weight_grams": f"{net_weight:.1f}",
        "servings": f"{servings}",
        "serving_weight_grams": f"{serving_weight:.1f}",
        "carbs_per_serving": f"{carbs_per_serving:.1f}",
    }

    return HTMLResponse(_render_page(pans, form=form_values, result=result))
