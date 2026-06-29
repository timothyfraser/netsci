"""Load credentials from .canvas/.env for Canvas and Cornell AI Gateway."""

import os
from pathlib import Path

GRADING_ROOT = Path(__file__).resolve().parent.parent
CANVAS_ROOT = GRADING_ROOT.parent / ".canvas"
DEFAULT_CANVAS_BASE = "https://canvas.cornell.edu"
DEFAULT_LITELLM_BASE = "https://api.ai.it.cornell.edu"


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


def load_env() -> None:
    load_dotenv(CANVAS_ROOT / ".env")
    load_dotenv(GRADING_ROOT / ".env")


def get_canvas_env() -> tuple[str, str, str]:
    load_env()
    base = os.environ.get("CANVAS_BASE_URL", DEFAULT_CANVAS_BASE).rstrip("/")
    token = os.environ.get("CANVAS_API_TOKEN") or os.environ.get("CANVAS_API_KEY", "")
    course = os.environ.get("CANVAS_COURSE_ID", "")
    return base, token, course


def get_litellm_env() -> tuple[str, str]:
    load_env()
    base = (
        os.environ.get("LITELLM_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or DEFAULT_LITELLM_BASE
    ).rstrip("/")
    key = (
        os.environ.get("LITELLM_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    )
    return base, key


def mock_llm_enabled() -> bool:
    load_env()
    return os.environ.get("MOCK_LLM", "").strip().lower() in ("1", "true", "yes")
