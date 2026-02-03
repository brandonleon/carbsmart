from html import escape

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PanCreate, PanUpdate
from app.repositories import pans as pans_repo

router = APIRouter()


def _render_page(
    pans,
    error: str | None = None,
    created: bool = False,
    updated: bool = False,
) -> str:
    rows = []
    for pan in pans:
        rows.append(
            """<tr>
                <td>{id}</td>
                <td>{name}</td>
                <td>{weight:.2f}</td>
                <td>{capacity}</td>
                <td>{notes}</td>
                <td><a href="/pans/{id}/edit">Edit</a></td>
            </tr>""".format(
                id=pan.id,
                name=escape(pan.name),
                weight=pan.weight_grams,
                capacity=escape(pan.capacity_label or ""),
                notes=escape(pan.notes or ""),
            )
        )

    status_html = ""
    if created:
        status_html = "<p class=\"notice\">Pan added.</p>"
    if updated:
        status_html = "<p class=\"notice\">Pan updated.</p>"
    if error:
        status_html = f"<p class=\"error\">{escape(error)}</p>"

    table_body = "\n".join(rows) if rows else "<tr><td colspan=\"6\">No pans yet.</td></tr>"

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>CarbSmart - Pans</title>
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
      p {{
        max-width: 48rem;
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
      input {{
        padding: 0.5rem 0.6rem;
        border-radius: 6px;
        border: 1px solid #ccb8a5;
        font-size: 1rem;
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
      table {{
        margin-top: 2rem;
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
      }}
      th, td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e5d6c7;
        text-align: left;
      }}
      th {{
        background: #f2e2d4;
      }}
      .notice {{
        color: #1b6b2a;
        font-weight: 600;
      }}
      .error {{
        color: #b3261e;
        font-weight: 600;
      }}
      .layout {{
        display: grid;
        gap: 2rem;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
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
      <a href="/pans">Pan Library</a>
      <a href="/calc">Serving Calculator</a>
    </nav>
    <h1>Pan Library</h1>
    <p>Store your pan weights once and re-use them for every recipe.</p>
    {status_html}
    <section class=\"layout\">
      <form method=\"post\" action=\"/pans\">
        <label>
          Pan name
          <input name=\"name\" required />
        </label>
        <label>
          Weight (grams)
          <input name=\"weight_grams\" type=\"number\" min=\"0\" step=\"0.1\" required />
        </label>
        <label>
          Capacity / Size (volume or pan size, e.g. 2 qt, 3 L, 11-inch)
          <input name=\"capacity_label\" />
        </label>
        <label>
          Notes
          <input name=\"notes\" />
        </label>
        <button type=\"submit\">Add pan</button>
      </form>
      <div>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Weight (g)</th>
              <th>Capacity</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {table_body}
          </tbody>
        </table>
      </div>
    </section>
  </body>
</html>"""


@router.get("/pans", response_class=HTMLResponse)
def pans_page(
    created: int | None = None,
    updated: int | None = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    pans = pans_repo.list_pans(db)
    return HTMLResponse(_render_page(pans, created=bool(created), updated=bool(updated)))


@router.post("/pans")
def create_pan(
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
        return HTMLResponse(
            _render_page(pans, error="Pan name + capacity already exists"),
            status_code=409,
        )

    return RedirectResponse(url="/pans?created=1", status_code=303)


@router.get("/pans/{pan_id}/edit", response_class=HTMLResponse)
def edit_pan_page(pan_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    pan = pans_repo.get_pan(db, pan_id)
    if not pan:
        raise HTTPException(status_code=404, detail="Pan not found")

    return HTMLResponse(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Edit Pan</title>
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
      input {{
        padding: 0.5rem 0.6rem;
        border-radius: 6px;
        border: 1px solid #ccb8a5;
        font-size: 1rem;
      }}
      .actions {{
        display: flex;
        gap: 0.75rem;
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
      a {{
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        border: 1px solid #6a3c1d;
        color: #6a3c1d;
        text-decoration: none;
      }}
    </style>
  </head>
  <body>
    <h1>Edit Pan</h1>
    <form method="post" action="/pans/{pan.id}">
      <label>
        Pan name
        <input name="name" value="{escape(pan.name)}" required />
      </label>
      <label>
        Weight (grams)
        <input name="weight_grams" type="number" min="0" step="0.1" value="{pan.weight_grams:.2f}" required />
      </label>
      <label>
        Capacity / Size (volume or pan size, e.g. 2 qt, 3 L, 11-inch)
        <input name="capacity_label" value="{escape(pan.capacity_label or "")}" />
      </label>
      <label>
        Notes
        <input name="notes" value="{escape(pan.notes or "")}" />
      </label>
      <div class="actions">
        <button type="submit">Save changes</button>
        <a href="/pans">Cancel</a>
      </div>
    </form>
  </body>
</html>"""
    )


@router.post("/pans/{pan_id}")
def update_pan(
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
        return HTMLResponse(
            _render_page(pans, error="Pan name + capacity already exists"),
            status_code=409,
        )

    return RedirectResponse(url="/pans?updated=1", status_code=303)
