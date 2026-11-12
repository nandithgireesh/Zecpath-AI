$env:PYTHONIOENCODING = "utf-8"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"

Write-Host "Running Unified Regression Test Suite (Days 21 - 28)..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py"
