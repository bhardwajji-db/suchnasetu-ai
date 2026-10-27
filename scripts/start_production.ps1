$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$env:HOST = "127.0.0.1"
$env:BACKEND_HOST = "127.0.0.1"
$env:PORT = "8000"
$env:APP_ENV = "production"
$env:ENABLE_API_DOCS = "false"
$env:AUTH_COOKIE_SECURE = "true"
$env:AUTH_SECRET_KEY = "suchnasetu-prod-secure-token-32chars-for-planb-demo-session"
$env:AUTH_PUBLIC_APP_URL = "https://ace-turned-deaf-suggesting.trycloudflare.com"
$env:CORS_ALLOWED_ORIGINS = "https://ace-turned-deaf-suggesting.trycloudflare.com,http://127.0.0.1:8000"

& .\.venv\Scripts\python.exe -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000
