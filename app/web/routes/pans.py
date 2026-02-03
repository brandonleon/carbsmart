from html import escape

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PanCreate, PanUpdate
from app.repositories import pans as pans_repo

router = APIRouter()

COMMON_HEAD = """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap"
    />
    <style>
      :root {
        --cs-font-sans: "Manrope", "Segoe UI", sans-serif;
        --cs-font-display: "Playfair Display", "Times New Roman", serif;
      }
      :root[data-bs-theme="light"] {
        color-scheme: light;
        --cs-base: #eff1f5;
        --cs-mantle: #e6e9ef;
        --cs-crust: #dce0e8;
        --cs-surface0: #ccd0da;
        --cs-surface1: #bcc0cc;
        --cs-surface2: #acb0be;
        --cs-overlay0: #9ca0b0;
        --cs-overlay1: #8c8fa1;
        --cs-overlay2: #7c7f93;
        --cs-text: #4c4f69;
        --cs-subtext0: #6c6f85;
        --cs-subtext1: #5c5f77;
        --cs-blue: #1e66f5;
        --cs-lavender: #7287fd;
        --cs-green: #40a02b;
        --cs-yellow: #df8e1d;
        --cs-red: #d20f39;
        --cs-mauve: #8839ef;
        --cs-rosewater: #dc8a78;
        --cs-peach: #fe640b;

        --bs-body-bg: var(--cs-base);
        --bs-body-color: var(--cs-text);
        --bs-secondary-color: var(--cs-subtext0);
        --bs-tertiary-bg: var(--cs-mantle);
        --bs-emphasis-color: var(--cs-text);
        --bs-border-color: var(--cs-surface2);
        --bs-link-color: var(--cs-blue);
        --bs-link-hover-color: var(--cs-lavender);
        --bs-primary: var(--cs-mauve);
        --bs-primary-rgb: 136, 57, 239;
        --bs-secondary: var(--cs-overlay1);
        --bs-secondary-rgb: 140, 143, 161;
        --bs-success: var(--cs-green);
        --bs-success-rgb: 64, 160, 43;
        --bs-danger: var(--cs-red);
        --bs-danger-rgb: 210, 15, 57;
        --bs-warning: var(--cs-yellow);
        --bs-warning-rgb: 223, 142, 29;
        --bs-info: var(--cs-blue);
        --bs-info-rgb: 30, 102, 245;
        --bs-card-bg: rgba(255, 255, 255, 0.82);
        --bs-card-border-color: var(--cs-surface2);
      }
      :root[data-bs-theme="dark"] {
        color-scheme: dark;
        --cs-base: #1e1e2e;
        --cs-mantle: #181825;
        --cs-crust: #11111b;
        --cs-surface0: #313244;
        --cs-surface1: #45475a;
        --cs-surface2: #585b70;
        --cs-overlay0: #6c7086;
        --cs-overlay1: #7f849c;
        --cs-overlay2: #9399b2;
        --cs-text: #cdd6f4;
        --cs-subtext0: #a6adc8;
        --cs-subtext1: #bac2de;
        --cs-blue: #89b4fa;
        --cs-lavender: #b4befe;
        --cs-green: #a6e3a1;
        --cs-yellow: #f9e2af;
        --cs-red: #f38ba8;
        --cs-mauve: #cba6f7;
        --cs-rosewater: #f5e0dc;
        --cs-peach: #fab387;

        --bs-body-bg: var(--cs-base);
        --bs-body-color: var(--cs-text);
        --bs-secondary-color: var(--cs-subtext0);
        --bs-tertiary-bg: var(--cs-mantle);
        --bs-emphasis-color: var(--cs-text);
        --bs-border-color: var(--cs-surface2);
        --bs-link-color: var(--cs-blue);
        --bs-link-hover-color: var(--cs-lavender);
        --bs-primary: var(--cs-mauve);
        --bs-primary-rgb: 203, 166, 247;
        --bs-secondary: var(--cs-overlay1);
        --bs-secondary-rgb: 127, 132, 156;
        --bs-success: var(--cs-green);
        --bs-success-rgb: 166, 227, 161;
        --bs-danger: var(--cs-red);
        --bs-danger-rgb: 243, 139, 168;
        --bs-warning: var(--cs-yellow);
        --bs-warning-rgb: 249, 226, 175;
        --bs-info: var(--cs-blue);
        --bs-info-rgb: 137, 180, 250;
        --bs-card-bg: rgba(24, 24, 37, 0.88);
        --bs-card-border-color: var(--cs-surface1);
      }
      body {
        font-family: var(--cs-font-sans);
        min-height: 100vh;
      }
      :root[data-bs-theme="light"] body {
        background:
          radial-gradient(900px 500px at 10% -10%, rgba(220, 138, 120, 0.25), transparent 60%),
          radial-gradient(700px 500px at 110% 0%, rgba(114, 135, 253, 0.2), transparent 60%),
          var(--bs-body-bg);
      }
      :root[data-bs-theme="dark"] body {
        background:
          radial-gradient(900px 500px at 10% -10%, rgba(203, 166, 247, 0.18), transparent 60%),
          radial-gradient(700px 500px at 110% 0%, rgba(137, 180, 250, 0.12), transparent 60%),
          var(--bs-body-bg);
      }
      .brand,
      h1,
      h2,
      .display-6,
      .headline {
        font-family: var(--cs-font-display);
        letter-spacing: 0.3px;
      }
      .navbar,
      .card {
        backdrop-filter: blur(10px);
      }
      .card {
        border-radius: 1.25rem;
      }
      .form-control,
      .form-select {
        border-radius: 0.85rem;
      }
      .btn {
        border-radius: 999px;
      }
      .table thead th {
        background: var(--bs-tertiary-bg);
        color: var(--bs-body-color);
      }
      @keyframes rise {
        from {
          opacity: 0;
          transform: translateY(12px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      .animate-rise {
        animation: rise 0.6s ease-out both;
      }
      .animate-delay-1 {
        animation-delay: 0.1s;
      }
      .animate-delay-2 {
        animation-delay: 0.2s;
      }
      .animate-delay-3 {
        animation-delay: 0.3s;
      }
      @media (prefers-reduced-motion: reduce) {
        .animate-rise {
          animation: none;
        }
      }
    </style>
"""

THEME_SCRIPT = """
    <script>
      (() => {
        const storageKey = "carbsmart-theme";
        const root = document.documentElement;
        const stored = localStorage.getItem(storageKey);
        const theme = stored || "light";
        root.setAttribute("data-bs-theme", theme);

        const toggle = document.getElementById("themeToggle");
        const label = document.getElementById("themeLabel");
        const update = () => {
          const current = root.getAttribute("data-bs-theme") || "light";
          if (label) {
            label.textContent = current === "dark" ? "Dark" : "Light";
          }
          if (toggle) {
            toggle.setAttribute("aria-pressed", current === "dark" ? "true" : "false");
          }
        };

        update();
        if (toggle) {
          toggle.addEventListener("click", () => {
            const current = root.getAttribute("data-bs-theme") || "light";
            const next = current === "light" ? "dark" : "light";
            root.setAttribute("data-bs-theme", next);
            localStorage.setItem(storageKey, next);
            update();
          });
        }
      })();
    </script>
"""


def _render_nav(active: str) -> str:
    pans_class = "btn btn-sm btn-primary" if active == "pans" else "btn btn-sm btn-outline-secondary"
    calc_class = "btn btn-sm btn-primary" if active == "calc" else "btn btn-sm btn-outline-secondary"
    return f"""
    <nav class="navbar bg-body-tertiary border rounded-4 shadow-sm px-3 py-2 animate-rise">
      <div class="container-fluid px-0">
        <a class="navbar-brand brand fw-semibold" href="/pans">CarbSmart</a>
        <div class="ms-auto d-flex flex-wrap gap-2 align-items-center">
          <a class="{pans_class}" href="/pans">Pan Library</a>
          <a class="{calc_class}" href="/calc">Serving Calculator</a>
          <button class="btn btn-sm btn-outline-secondary" type="button" id="themeToggle" aria-pressed="false">
            Theme: <span id="themeLabel">Light</span>
          </button>
        </div>
      </div>
    </nav>
    """


def _render_page(
    pans,
    error: str | None = None,
    created: bool = False,
    updated: bool = False,
) -> str:
    rows = []
    for pan in pans:
        capacity = (
            escape(pan.capacity_label)
            if pan.capacity_label
            else "<span class=\"text-secondary\">-</span>"
        )
        notes = escape(pan.notes) if pan.notes else "<span class=\"text-secondary\">-</span>"
        rows.append(
            f"""<tr>
                <td class=\"fw-semibold\">{pan.id}</td>
                <td>{escape(pan.name)}</td>
                <td>{pan.weight_grams:.2f}</td>
                <td>{capacity}</td>
                <td>{notes}</td>
                <td><a class=\"btn btn-sm btn-outline-primary\" href=\"/pans/{pan.id}/edit\">Edit</a></td>
            </tr>"""
        )

    status_html = ""
    if created:
        status_html = (
            "<div class=\"alert alert-success mt-3 animate-rise animate-delay-1\" role=\"alert\">Pan added.</div>"
        )
    if updated:
        status_html = (
            "<div class=\"alert alert-success mt-3 animate-rise animate-delay-1\" role=\"alert\">Pan updated.</div>"
        )
    if error:
        status_html = (
            f"<div class=\"alert alert-danger mt-3 animate-rise animate-delay-1\" "
            f"role=\"alert\">{escape(error)}</div>"
        )

    if rows:
        table_body = "\n".join(rows)
    else:
        table_body = (
            "<tr><td colspan=\"6\" class=\"text-center text-secondary py-4\">No pans yet.</td></tr>"
        )

    pans_count = len(pans)

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>CarbSmart - Pans</title>
{COMMON_HEAD}
  </head>
  <body>
    <main class=\"container py-4\">
      {_render_nav("pans")}
      <header class=\"mt-4 mb-3 animate-rise animate-delay-1\">
        <p class=\"text-uppercase text-secondary fw-semibold small mb-2\">Prep once, cook often</p>
        <h1 class=\"display-6 mb-2\">Pan Library</h1>
        <p class=\"text-secondary mb-0\">Store your pan weights once and re-use them for every recipe.</p>
      </header>
      {status_html}
      <section class=\"row g-4 align-items-start mt-1\">
        <div class=\"col-lg-4\">
          <div class=\"card shadow-sm border-0 animate-rise animate-delay-2\">
            <div class=\"card-body\">
              <div class=\"d-flex align-items-center justify-content-between mb-3\">
                <h2 class=\"h5 mb-0\">Add a pan</h2>
                <span class=\"badge text-bg-primary\">New</span>
              </div>
              <form class=\"vstack gap-3\" method=\"post\" action=\"/pans\">
                <div>
                  <label class=\"form-label\">Pan name</label>
                  <input class=\"form-control\" name=\"name\" required />
                </div>
                <div>
                  <label class=\"form-label\">Weight (grams)</label>
                  <input class=\"form-control\" name=\"weight_grams\" type=\"number\" min=\"0\" step=\"0.1\" required />
                </div>
                <div>
                  <label class=\"form-label\">Capacity / Size (volume or pan size, e.g. 2 qt, 3 L)</label>
                  <input
                    class=\"form-control\"
                    name=\"capacity_label\"
                    placeholder=\"Optional\"
                  />
                </div>
                <div>
                  <label class=\"form-label\">Notes</label>
                  <input class=\"form-control\" name=\"notes\" placeholder=\"Optional\" />
                </div>
                <button class=\"btn btn-primary\" type=\"submit\">Add pan</button>
              </form>
            </div>
          </div>
        </div>
        <div class=\"col-lg-8\">
          <div class=\"card shadow-sm border-0 animate-rise animate-delay-3\">
            <div class=\"card-body\">
              <div class=\"d-flex align-items-center justify-content-between\">
                <h2 class=\"h5 mb-0\">Saved pans</h2>
                <span class=\"badge text-bg-secondary\">{pans_count} total</span>
              </div>
            </div>
            <div class=\"table-responsive\">
              <table class=\"table table-hover align-middle mb-0\">
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
          </div>
        </div>
      </section>
    </main>
{THEME_SCRIPT}
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
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Edit Pan</title>
{COMMON_HEAD}
  </head>
  <body>
    <main class=\"container py-4\">
      {_render_nav("pans")}
      <header class=\"mt-4 mb-3 animate-rise animate-delay-1\">
        <p class=\"text-uppercase text-secondary fw-semibold small mb-2\">Update details</p>
        <h1 class=\"display-6 mb-2\">Edit Pan</h1>
        <p class=\"text-secondary mb-0\">Update the details and save when you are ready.</p>
      </header>
      <section class=\"row justify-content-center\">
        <div class=\"col-lg-6\">
          <div class=\"card shadow-sm border-0 animate-rise animate-delay-2\">
            <div class=\"card-body\">
              <form class=\"vstack gap-3\" method=\"post\" action=\"/pans/{pan.id}\">
                <div>
                  <label class=\"form-label\">Pan name</label>
                  <input class=\"form-control\" name=\"name\" value=\"{escape(pan.name)}\" required />
                </div>
                <div>
                  <label class=\"form-label\">Weight (grams)</label>
                  <input
                    class=\"form-control\"
                    name=\"weight_grams\"
                    type=\"number\"
                    min=\"0\"
                    step=\"0.1\"
                    value=\"{pan.weight_grams:.2f}\"
                    required
                  />
                </div>
                <div>
                  <label class=\"form-label\">Capacity / Size (volume or pan size, e.g. 2 qt, 3 L)</label>
                  <input
                    class=\"form-control\"
                    name=\"capacity_label\"
                    value=\"{escape(pan.capacity_label or '')}\"
                  />
                </div>
                <div>
                  <label class=\"form-label\">Notes</label>
                  <input class=\"form-control\" name=\"notes\" value=\"{escape(pan.notes or '')}\" />
                </div>
                <div class=\"d-flex flex-wrap gap-2\">
                  <button class=\"btn btn-primary\" type=\"submit\">Save changes</button>
                  <a class=\"btn btn-outline-secondary\" href=\"/pans\">Cancel</a>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>
    </main>
{THEME_SCRIPT}
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
