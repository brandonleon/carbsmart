from html import escape

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories import pans as pans_repo
from app.services.calc import calculate_plan

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
        status_html = (
            f"<div class=\"alert alert-danger mt-3 animate-rise animate-delay-1\" "
            f"role=\"alert\">{escape(error)}</div>"
        )

    if result:
        result_html = f"""
          <div class=\"card shadow-sm border-0 h-100 animate-rise animate-delay-3\">
            <div class=\"card-body\">
              <div class=\"d-flex align-items-center justify-content-between mb-3\">
                <h2 class=\"h5 mb-0\">Results</h2>
                <span class=\"badge text-bg-success\">Ready</span>
              </div>
              <dl class=\"row gy-2 mb-0\">
                <dt class=\"col-7 text-secondary\">Net cooked weight</dt>
                <dd class=\"col-5 text-end fw-semibold\">{result['net_weight_grams']} g</dd>
                <dt class=\"col-7 text-secondary\">Servings</dt>
                <dd class=\"col-5 text-end fw-semibold\">{result['servings']}</dd>
                <dt class=\"col-7 text-secondary\">Serving weight</dt>
                <dd class=\"col-5 text-end fw-semibold\">{result['serving_weight_grams']} g</dd>
                <dt class=\"col-7 text-secondary\">Carbs per serving</dt>
                <dd class=\"col-5 text-end fw-semibold\">{result['carbs_per_serving']} g</dd>
              </dl>
            </div>
          </div>
        """
    else:
        result_html = """
          <div class="card shadow-sm border-0 h-100 animate-rise animate-delay-3">
            <div class="card-body">
              <h2 class="h5">How it works</h2>
              <p class="text-secondary mb-3">
                We subtract your pan weight from the total, then divide by your serving range to recommend even
                portions.
              </p>
              <div class="d-flex flex-wrap gap-2">
                <span class="badge text-bg-secondary">Accurate</span>
                <span class="badge text-bg-secondary">Fast</span>
                <span class="badge text-bg-secondary">Repeatable</span>
              </div>
            </div>
          </div>
        """

    empty_state = ""
    if not pans:
        empty_state = (
            "<div class=\"alert alert-info mt-3 animate-rise animate-delay-1\" role=\"alert\">"
            "Add a pan first to enable calculations. "
            "<a class=\"alert-link\" href=\"/pans\">Go to pan library</a>."
            "</div>"
        )

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>CarbSmart - Serving Calculator</title>
{COMMON_HEAD}
  </head>
  <body>
    <main class=\"container py-4\">
      {_render_nav("calc")}
      <header class=\"mt-4 mb-3 animate-rise animate-delay-1\">
        <p class=\"text-uppercase text-secondary fw-semibold small mb-2\">Kitchen math, simplified</p>
        <h1 class=\"display-6 mb-2\">Serving Calculator</h1>
        <p class=\"text-secondary mb-0\">
          Enter the total cooked weight with the pan and get precise serving sizes.
        </p>
      </header>
      {status_html}
      {empty_state}
      <section class=\"row g-4 align-items-start mt-1\">
        <div class=\"col-lg-5\">
          <div class=\"card shadow-sm border-0 animate-rise animate-delay-2\">
            <div class=\"card-body\">
              <div class=\"d-flex align-items-center justify-content-between mb-3\">
                <h2 class=\"h5 mb-0\">Inputs</h2>
                <span class=\"badge text-bg-primary\">Step 1</span>
              </div>
              <form class=\"vstack gap-3\" method=\"post\" action=\"/calc\">
                <div>
                  <label class=\"form-label\">Pan</label>
                  <select class=\"form-select\" name=\"pan_id\" required>
                    {options_html}
                  </select>
                </div>
                <div>
                  <label class=\"form-label\">Total weight (pan + food) in grams</label>
                  <input
                    class=\"form-control\"
                    name=\"total_weight_grams\"
                    type=\"number\"
                    min=\"0\"
                    step=\"0.1\"
                    value=\"{escape(form.get('total_weight_grams', ''))}\"
                    required
                  />
                </div>
                <div>
                  <label class=\"form-label\">Total carbs (grams)</label>
                  <input
                    class=\"form-control\"
                    name=\"total_carbs\"
                    type=\"number\"
                    min=\"0\"
                    step=\"0.1\"
                    value=\"{escape(form.get('total_carbs', ''))}\"
                    required
                  />
                </div>
                <div>
                  <label class=\"form-label\">Target serving min (grams)</label>
                  <input
                    class=\"form-control\"
                    name=\"target_min_grams\"
                    type=\"number\"
                    min=\"0\"
                    step=\"1\"
                    value=\"{escape(form.get('target_min_grams', '200'))}\"
                    required
                  />
                </div>
                <div>
                  <label class=\"form-label\">Target serving max (grams)</label>
                  <input
                    class=\"form-control\"
                    name=\"target_max_grams\"
                    type=\"number\"
                    min=\"0\"
                    step=\"1\"
                    value=\"{escape(form.get('target_max_grams', '300'))}\"
                    required
                  />
                </div>
                <button class=\"btn btn-primary\" type=\"submit\">Calculate servings</button>
              </form>
            </div>
          </div>
        </div>
        <div class=\"col-lg-7\">
{result_html}
        </div>
      </section>
    </main>
{THEME_SCRIPT}
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
