from pathlib import Path

from fastapi.templating import Jinja2Templates

from app import __version__

_templates_dir = Path(__file__).resolve().parent.parent / "templates"

templates = Jinja2Templates(directory=str(_templates_dir))
templates.env.globals["version"] = __version__
