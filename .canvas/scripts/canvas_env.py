"""Load Canvas API credentials from environment and optional .canvas/.env."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://canvas.cornell.edu"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = val


def get_canvas_env():
    load_dotenv(ROOT / ".env")
    base = os.environ.get("CANVAS_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    token = os.environ.get("CANVAS_API_TOKEN") or os.environ.get("CANVAS_API_KEY", "")
    course = os.environ.get("CANVAS_COURSE_ID", "")
    return base, token, course
