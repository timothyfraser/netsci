# Classbot Grading Dashboard — start local server
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}
$env:MOCK_LLM = if ($env:MOCK_LLM) { $env:MOCK_LLM } else { "0" }
.\.venv\Scripts\python app\server.py
