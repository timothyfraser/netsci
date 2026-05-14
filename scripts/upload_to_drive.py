"""Upload build/notebooklm-source.md to Google Drive as a native Google Doc.

Updates the file in place if a Doc with the target name already exists in the
target folder, so the Drive file ID stays stable for NotebookLM.

Required env vars:
    GDRIVE_SERVICE_ACCOUNT_JSON  Full JSON contents of a service-account key
    GDRIVE_FOLDER_ID             ID of the destination Drive folder

Optional env vars:
    GDRIVE_DOC_NAME              Name of the Doc (default below)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "build" / "notebooklm-source.md"
DEFAULT_DOC_NAME = "SYSEN 5470 — Course Content (NotebookLM Source)"
SCOPES = ["https://www.googleapis.com/auth/drive"]


def must_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        print(f"Missing required env var: {name}", file=sys.stderr)
        sys.exit(2)
    return val


def main() -> int:
    if not SOURCE.exists():
        print(f"Source not built: {SOURCE}", file=sys.stderr)
        return 1

    sa_json = must_env("GDRIVE_SERVICE_ACCOUNT_JSON")
    folder_id = must_env("GDRIVE_FOLDER_ID")
    doc_name = os.environ.get("GDRIVE_DOC_NAME", DEFAULT_DOC_NAME)

    creds = service_account.Credentials.from_service_account_info(
        json.loads(sa_json), scopes=SCOPES
    )
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    # Drive query strings need single quotes escaped.
    safe_name = doc_name.replace("'", "\\'")
    query = (
        f"'{folder_id}' in parents and name = '{safe_name}' "
        "and trashed = false"
    )
    existing = (
        drive.files()
        .list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
        .get("files", [])
    )

    media = MediaFileUpload(str(SOURCE), mimetype="text/markdown", resumable=False)

    if existing:
        file_id = existing[0]["id"]
        result = (
            drive.files()
            .update(
                fileId=file_id,
                media_body=media,
                fields="id, name, webViewLink, modifiedTime",
                supportsAllDrives=True,
            )
            .execute()
        )
        action = "updated"
    else:
        result = (
            drive.files()
            .create(
                body={
                    "name": doc_name,
                    "parents": [folder_id],
                    "mimeType": "application/vnd.google-apps.document",
                },
                media_body=media,
                fields="id, name, webViewLink, modifiedTime",
                supportsAllDrives=True,
            )
            .execute()
        )
        action = "created"

    link = result.get("webViewLink", "(no webViewLink returned)")
    print(f"{action}: {result['name']} ({result['id']}) -> {link}")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(
                f"### NotebookLM source synced\n\n"
                f"- **Action:** {action}\n"
                f"- **File:** {result['name']}\n"
                f"- **Drive link:** {link}\n"
                f"- **Modified:** {result.get('modifiedTime', '?')}\n"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
