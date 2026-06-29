"""Extract plain text from PDFs, Word docs, and Canvas submission bodies."""

from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

_DOCX_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def html_to_text(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required for PDF extraction") from exc
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n\n".join(parts).strip()


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    paras: list[str] = []
    for para in root.iter(f"{_W_NS}p"):
        texts = [node.text for node in para.iter(f"{_W_NS}t") if node.text]
        if texts:
            paras.append("".join(texts))
    return "\n\n".join(paras).strip()


def extract_file_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(path)
    if suffix == ".docx":
        return extract_docx_text(path)
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def extract_submission_text(report_path: Path | None, body_html: str = "") -> str:
    chunks: list[str] = []
    if body_html:
        chunks.append(html_to_text(body_html))
    if report_path and report_path.is_file():
        chunks.append(extract_file_text(report_path))
    return "\n\n---\n\n".join(c for c in chunks if c).strip()
