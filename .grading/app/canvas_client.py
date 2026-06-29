"""Canvas submission sync, cache, and grade publish."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests

from env import GRADING_ROOT, get_canvas_env
from extract_text import extract_submission_text
from rubric import get_assignment

CACHE_ROOT = GRADING_ROOT / "cache" / "submissions"
SESSION = requests.Session()


def _headers() -> dict[str, str]:
    _, token, _ = get_canvas_env()
    return {"Authorization": f"Bearer {token}"}


def _api(path: str, params: dict[str, Any] | None = None) -> Any:
    base, token, _ = get_canvas_env()
    if not token:
        raise RuntimeError("CANVAS_API_KEY not set in .canvas/.env")
    url = f"{base}/api/v1{path}"
    resp = SESSION.get(url, headers=_headers(), params=params or {}, timeout=120)
    resp.raise_for_status()
    return resp.json()


def _api_paginated(path: str, params: dict[str, Any] | None = None) -> list[Any]:
    base, token, _ = get_canvas_env()
    if not token:
        raise RuntimeError("CANVAS_API_KEY not set in .canvas/.env")
    url = f"{base}/api/v1{path}"
    out: list[Any] = []
    while url:
        resp = SESSION.get(url, headers=_headers(), params=params, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            out.extend(data)
        else:
            out.append(data)
            break
        link = resp.headers.get("Link", "")
        url = ""
        params = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part[part.find("<") + 1 : part.find(">")]
                break
        time.sleep(0.05)
    return out


def _put_submission(course: str, assignment_id: int, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    base, token, _ = get_canvas_env()
    url = f"{base}/api/v1/courses/{course}/assignments/{assignment_id}/submissions/{user_id}"
    resp = SESSION.put(url, headers=_headers(), json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def _put_submission_form(
    course: str, assignment_id: int, user_id: int, form: dict[str, Any]
) -> dict[str, Any]:
    """Canvas reliably accepts comment + grade as x-www-form-urlencoded bracket keys."""
    base, token, _ = get_canvas_env()
    url = f"{base}/api/v1/courses/{course}/assignments/{assignment_id}/submissions/{user_id}"
    resp = SESSION.put(url, headers=_headers(), data=form, timeout=120)
    resp.raise_for_status()
    return resp.json()


def _netid_from_user(user: dict[str, Any]) -> str:
    for key in ("sis_user_id", "login_id", "short_name"):
        val = user.get(key)
        if val and isinstance(val, str):
            return val.split("@")[0]
    email = user.get("email") or ""
    if email:
        return email.split("@")[0]
    return str(user.get("id", ""))


def _attachment_filename(att: dict[str, Any]) -> str:
    return (att.get("filename") or "report.pdf").replace("+", " ")


def _pick_report_attachment(attachments: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Choose the best report-like attachment (PDF or Word preferred)."""
    if not attachments:
        return None

    report_hints = ("report", "case study", "case_study", "project", "centrality", "sysen", "paper")

    def score(att: dict[str, Any]) -> int:
        filename = (att.get("filename") or "").lower().replace("+", " ")
        ctype = (att.get("content-type") or "").lower()
        points = 0
        if filename.endswith(".pdf") or "pdf" in ctype:
            points += 20
        elif filename.endswith(".docx") or "wordprocessingml" in ctype:
            points += 18
        elif filename.endswith(".doc") or "msword" in ctype:
            points += 16
        elif filename.endswith((".txt", ".md")):
            points += 8
        else:
            return -1
        for hint in report_hints:
            if hint in filename:
                points += 6
        return points

    ranked = sorted(attachments, key=score, reverse=True)
    best = ranked[0]
    return best if score(best) >= 0 else None


def _fetch_submission_detail(course: str, assignment_id: int, user_id: int) -> dict[str, Any]:
    return _api(
        f"/courses/{course}/assignments/{assignment_id}/submissions/{user_id}",
        {"include[]": ["submission_history"]},
    )


def _download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = SESSION.get(url, headers=_headers(), timeout=180, stream=True)
    resp.raise_for_status()
    with dest.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)


def _submission_key(assignment_key: str, user_id: int, attempt: int) -> str:
    return f"{assignment_key}_{user_id}_a{attempt}"


def sync_assignment(assignment_key: str, *, force: bool = False) -> list[dict[str, str]]:
    assignment = get_assignment(assignment_key)
    if not assignment:
        raise ValueError(f"Unknown assignment_key: {assignment_key}")
    _, _, course = get_canvas_env()
    if not course:
        raise RuntimeError("CANVAS_COURSE_ID not set in .canvas/.env")

    aid = assignment["canvas_assignment_id"]
    subs = _api_paginated(
        f"/courses/{course}/assignments/{aid}/submissions",
        {
            "include[]": ["user", "submission_history"],
            "per_page": 100,
        },
    )

    from csv_store import get_row, upsert_row

    rows: list[dict[str, str]] = []
    for sub in subs:
        if sub.get("workflow_state") in ("unsubmitted", "deleted"):
            continue
        user = sub.get("user") or {}
        user_id = int(sub.get("user_id") or user.get("id") or 0)
        if not user_id:
            continue

        # List endpoint often omits attachments; fetch full submission when needed.
        if not sub.get("attachments") and not sub.get("body") and sub.get("submitted_at"):
            sub = _fetch_submission_detail(course, aid, user_id)

        attempt = int(sub.get("attempt") or 1)
        key = _submission_key(assignment_key, user_id, attempt)
        cache_dir = CACHE_ROOT / assignment_key / str(user_id)
        cache_dir.mkdir(parents=True, exist_ok=True)

        report_path = ""
        text_path = cache_dir / "report.txt"
        body_html = sub.get("body") or ""

        if body_html and (force or not (cache_dir / "submission_body.html").is_file()):
            (cache_dir / "submission_body.html").write_text(body_html, encoding="utf-8")

        attachments = sub.get("attachments") or []
        att = _pick_report_attachment(attachments)
        if att:
            filename = _attachment_filename(att)
            local_report = cache_dir / filename
            legacy_report = cache_dir / (att.get("filename") or filename)
            if not local_report.is_file() and legacy_report.is_file():
                local_report = legacy_report
            if force or not local_report.is_file():
                file_url = att.get("url") or ""
                if file_url:
                    _download_file(file_url, local_report)
            if local_report.is_file():
                report_path = str(local_report)

        for att in attachments:
            fname = _attachment_filename(att)
            local = cache_dir / fname
            legacy = cache_dir / (att.get("filename") or fname)
            if not local.is_file() and legacy.is_file():
                local = legacy
            if not local.is_file() and att.get("url"):
                _download_file(att["url"], local)

        extracted = extract_submission_text(
            Path(report_path) if report_path else None,
            body_html,
        )
        if extracted and (force or not text_path.is_file()):
            text_path.write_text(extracted, encoding="utf-8")

        name = user.get("sortable_name") or user.get("name") or ""
        existing = get_row(key)
        payload: dict[str, Any] = {
            "submission_key": key,
            "student_name": name,
            "student_netid": _netid_from_user(user),
            "canvas_user_id": str(user_id),
            "canvas_submission_id": str(sub.get("id", "")),
            "assignment_key": assignment_key,
            "assignment_name": assignment["name"],
            "canvas_assignment_id": str(aid),
            "submitted_at": sub.get("submitted_at") or "",
            "attempt_number": str(attempt),
            "late": "true" if sub.get("late") else "false",
            "workflow_state": sub.get("workflow_state") or "",
            "cached_dir": str(cache_dir),
            "cached_report_path": report_path,
            "cached_text_path": str(text_path) if text_path.is_file() else "",
        }
        if not existing:
            payload["llm_status"] = "pending"
            payload["status"] = "synced"
        row = upsert_row(payload)
        rows.append(row)
    return rows


def publish_grade(
    row: dict[str, str],
    grade: str,
    comment: str,
) -> dict[str, Any]:
    _, _, course = get_canvas_env()
    aid = int(row["canvas_assignment_id"])
    uid = int(row["canvas_user_id"])
    attempt = int(row.get("attempt_number") or 1)

    form: dict[str, Any] = {"submission[posted_grade]": grade}
    comment = (comment or "").strip()
    if comment:
        form["comment[text_comment]"] = comment
        form["comment[attempt]"] = attempt

    result = _put_submission_form(course, aid, uid, form)
    comments = result.get("submission_comments") or []
    if comment and not comments:
        raise RuntimeError(
            "Canvas accepted grade but returned no submission_comments — comment may not have posted"
        )
    return result
