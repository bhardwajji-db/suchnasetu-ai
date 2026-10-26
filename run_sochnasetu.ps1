<#
.SYNOPSIS
    SochnaSetu AI — Unified Windows Master Launcher with Automatic Ollama Lifecycle & Clean Shutdown
.DESCRIPTION
    1. Checks if Ollama is running at http://127.0.0.1:11434.
       - If already running, preserves external Ollama and will NOT terminate it on shutdown.
       - If not running, starts Ollama as a managed child process and tracks its PID.
    2. Probes Ollama readiness and checks if the configured local model (gemma4:latest) is installed.
       - If missing, warns with exact installation instructions without unconsented background downloads.
       - If present, sends a lightweight readiness ping to ensure weights are accessible.
    3. Launches FastAPI backend daemon and React 19 / Vite frontend.
    4. Opens the default browser at http://localhost:5173.
    5. On Ctrl+C / Exit: Gracefully terminates frontend, backend, and stops Ollama ONLY if spawned by this launcher.
#>

param (
    [switch]$NoBrowser = $false,
    [string]$HostAddress = "0.0.0.0",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [string]$OllamaUrl = "http://127.0.0.1:11434",
    [string]$TargetModel = "gemma4:latest"
)

$ErrorActionPreference = "Stop"

# Set Project Root
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot

# State tracking for clean shutdown
$Global:OllamaPreExisting = $false
$Global:OllamaProcess = $null
$Global:BackendProcess = $null
$Global:FrontendProcess = $null
$Global:IsShuttingDown = $false

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "       SOCHNASETU AI -- MASTER LIFECYCLE & APPLICATION LAUNCHER       " -ForegroundColor Cyan
Write-Host "                 Notice-to-Action Accessibility Suite                 " -ForegroundColor DarkCyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# Function: Clean Shutdown Handler
# -----------------------------------------------------------------------------
function Stop-SochnaSetuServices {
    if ($Global:IsShuttingDown) { return }
    $Global:IsShuttingDown = $true

    Write-Host "`n----------------------------------------------------------------------" -ForegroundColor Yellow
    Write-Host " [SHUTDOWN] Initiating graceful shutdown of SochnaSetu AI services..." -ForegroundColor Yellow
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Yellow

    # 1. Check for active backend analysis requests
    try {
        $activeCheck = Invoke-RestMethod -Uri "http://127.0.0.1:$BackendPort/api/status/active-requests" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($activeCheck -and $activeCheck.active_requests -gt 0) {
            Write-Host " [WAIT] Waiting up to 5s for $($activeCheck.active_requests) in-flight analysis requests..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    } catch {}

    # 2. Attempt model memory unload from VRAM/RAM
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:$BackendPort/api/ollama/unload" -Method Post -TimeoutSec 2 -ErrorAction SilentlyContinue | Out-Null
        Write-Host " [OK] Ollama model memory unload request dispatched." -ForegroundColor Green
    } catch {}

    # 3. Terminate Frontend process
    if ($Global:FrontendProcess) {
        Write-Host " [SHUTDOWN] Stopping React frontend (PID: $($Global:FrontendProcess.Id))..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $Global:FrontendProcess.Id -Force -ErrorAction SilentlyContinue
            & taskkill /PID $Global:FrontendProcess.Id /T /F 2>$null | Out-Null
        } catch {}
    }

    # 4. Terminate Backend process
    if ($Global:BackendProcess) {
        Write-Host " [SHUTDOWN] Stopping FastAPI backend (PID: $($Global:BackendProcess.Id))..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $Global:BackendProcess.Id -Force -ErrorAction SilentlyContinue
            & taskkill /PID $Global:BackendProcess.Id /T /F 2>$null | Out-Null
        } catch {}
    }

    # 5. Clean up Ollama process strictly based on ownership
    if ($Global:OllamaPreExisting) {
        Write-Host " [PRESERVED] Pre-existing external Ollama daemon left running at $OllamaUrl." -ForegroundColor Green
    } else {
        if ($Global:OllamaProcess) {
            Write-Host " [SHUTDOWN] Stopping launcher-spawned Ollama daemon (PID: $($Global:OllamaProcess.Id))..." -ForegroundColor Yellow
            try {
                Stop-Process -Id $Global:OllamaProcess.Id -Force -ErrorAction SilentlyContinue
                & taskkill /PID $Global:OllamaProcess.Id /T /F 2>$null | Out-Null
            } catch {}
            Write-Host " [OK] Managed Ollama server terminated." -ForegroundColor Green
        }
    }

    # 6. Clean up launcher lockfile if present
    $lockFile = Join-Path $ProjectRoot ".launcher_pids.json"
    if (Test-Path $lockFile) {
        Remove-Item -Path $lockFile -Force -ErrorAction SilentlyContinue
    }

    Write-Host " [DONE] All prototype processes stopped cleanly. Exiting." -ForegroundColor Cyan
}

# Register Ctrl+C & SIGINT handlers
[Console]::TreatControlCAsInput = $false
Register-EngineEvent -SourceIdentifier ([System.Management.Automation.PsEngineEvent]::Exiting) -Action {
    Stop-SochnaSetuServices
} | Out-Null

try {
    # -------------------------------------------------------------------------
    # Step 1: Environment Pre-Flight
    # -------------------------------------------------------------------------
    Write-Host "[1/5] Checking environment dependencies..." -ForegroundColor White
    $PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $PythonExe)) {
        Write-Host " [ERROR] Python virtual environment not found at .venv\Scripts\python.exe." -ForegroundColor Red
        Write-Host "         Please run .\scripts\setup.ps1 first." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "       Python environment: $PythonExe [OK]" -ForegroundColor Green

    $NpmCmd = Get-Command "npm.cmd" -ErrorAction SilentlyContinue
    if (-not $NpmCmd) { $NpmCmd = Get-Command "npm" -ErrorAction SilentlyContinue }
    if (-not $NpmCmd) {
        Write-Host " [ERROR] Node.js / npm not found in system PATH." -ForegroundColor Red
        exit 1
    }
    Write-Host "       Node.js / npm: $($NpmCmd.Source) [OK]" -ForegroundColor Green

    # -------------------------------------------------------------------------
    # Step 2: Ollama Lifecycle & Model Readiness
    # -------------------------------------------------------------------------
    Write-Host "`n[2/5] Inspecting Local AI Server (Ollama at $OllamaUrl)..." -ForegroundColor White
    
    $ollamaRunning = $false
    try {
        $tagsResp = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
        $ollamaRunning = $true
    } catch {
        $ollamaRunning = $false
    }

    if ($ollamaRunning) {
        $Global:OllamaPreExisting = $true
        Write-Host "       Status: [Running] Pre-existing Ollama daemon detected." -ForegroundColor Green
        Write-Host "       Ownership: External process (will NOT be killed on prototype close)." -ForegroundColor DarkGreen
    } else {
        $Global:OllamaPreExisting = $false
        Write-Host "       Status: [Offline] Ollama is not running." -ForegroundColor Yellow
        Write-Host "       Action: State -> Starting Ollama..." -ForegroundColor Cyan

        # Locate ollama executable
        $ollamaExe = (Get-Command "ollama.exe" -ErrorAction SilentlyContinue).Source
        if (-not $ollamaExe) {
            $candidatePath = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
            if (Test-Path $candidatePath) { $ollamaExe = $candidatePath }
        }
        if (-not $ollamaExe) {
            $candidatePath = "C:\Program Files\Ollama\ollama.exe"
            if (Test-Path $candidatePath) { $ollamaExe = $candidatePath }
        }

        if ($ollamaExe) {
            Write-Host "       Found Ollama executable: $ollamaExe" -ForegroundColor Gray
            $Global:OllamaProcess = Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden -PassThru
            Write-Host "       Spawned Ollama process (PID: $($Global:OllamaProcess.Id))." -ForegroundColor Gray

            # Wait for Ollama to become responsive
            $attempts = 0
            $maxAttempts = 15
            while ($attempts -lt $maxAttempts) {
                Start-Sleep -Seconds 1
                $attempts++
                try {
                    $tagsResp = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
                    $ollamaRunning = $true
                    break
                } catch {}
            }

            if ($ollamaRunning) {
                Write-Host "       State: Starting Ollama -> Ready [OK]" -ForegroundColor Green
            } else {
                Write-Host "       [WARNING] Ollama did not respond within ${maxAttempts}s. Continuing with rule-based fallback." -ForegroundColor Yellow
            }
        } else {
            Write-Host "       [WARNING] Ollama executable not found. The app will run in rule-based fallback mode." -ForegroundColor Yellow
        }
    }

    # Model Presence & Readiness Probe
    if ($ollamaRunning) {
        Write-Host "       Action: State -> Checking model ($TargetModel)..." -ForegroundColor Cyan
        $modelFound = $false
        try {
            $tagsResp = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 4 -ErrorAction Stop
            if ($tagsResp -and $tagsResp.models) {
                foreach ($m in $tagsResp.models) {
                    $mName = $m.name
                    if ($mName -eq $TargetModel -or $mName -eq ($TargetModel.Split(':')[0]) -or $mName.StartsWith($TargetModel)) {
                        $modelFound = $true
                        break
                    }
                }
            }
        } catch {}

        if ($modelFound) {
            Write-Host "       State: Checking model -> Found ($TargetModel) [OK]" -ForegroundColor Green
            Write-Host "       Action: State -> Loading model / Readiness check..." -ForegroundColor Cyan
            try {
                # Lightweight warmup probe (single token prediction)
                $warmupPayload = @{
                    model = $TargetModel
                    messages = @(@{ role = "user"; content = "ping" })
                    stream = $false
                    keep_alive = "5m"
                    options = @{ num_predict = 1 }
                } | ConvertTo-Json
                $warmupResp = Invoke-RestMethod -Uri "$OllamaUrl/api/chat" -Method Post -Body $warmupPayload -ContentType "application/json" -TimeoutSec 15 -ErrorAction Stop
                Write-Host "       State: Loading model -> Ready! Model '$TargetModel' active in memory [OK]" -ForegroundColor Green
            } catch {
                Write-Host "       State: Model is pulled but initial warm-up timed out (weights will load on first query)." -ForegroundColor Yellow
            }
        } else {
            Write-Host "       State: Error -> Model missing" -ForegroundColor Red
            Write-Host "       ------------------------------------------------------------------" -ForegroundColor Red
            Write-Host "       [NOTICE] Model '$TargetModel' is NOT installed in Ollama." -ForegroundColor Yellow
            Write-Host "       To pull without unconsented multi-GB automatic downloads, run:" -ForegroundColor White
            Write-Host "         ollama run $TargetModel" -ForegroundColor Cyan
            Write-Host "       The application will start; rule-based analysis remains active." -ForegroundColor Yellow
            Write-Host "       ------------------------------------------------------------------" -ForegroundColor Red
        }
    }

    # Prepare log directory
    $logDir = Join-Path $ProjectRoot "data\logs"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $beOutLog = Join-Path $logDir "backend_stdout.log"
    $beErrLog = Join-Path $logDir "backend_stderr.log"
    $feOutLog = Join-Path $logDir "frontend_stdout.log"
    $feErrLog = Join-Path $logDir "frontend_stderr.log"

    # -------------------------------------------------------------------------
    # Step 3: Launch FastAPI Backend Server
    # -------------------------------------------------------------------------
    Write-Host "`n[3/5] Starting FastAPI Backend Server on port $BackendPort..." -ForegroundColor White
    $backendArgs = "-m uvicorn notice2action.api.server:app --app-dir src --host $HostAddress --port $BackendPort"
    $Global:BackendProcess = Start-Process -FilePath $PythonExe -ArgumentList $backendArgs -WorkingDirectory $ProjectRoot -RedirectStandardOutput $beOutLog -RedirectStandardError $beErrLog -PassThru -WindowStyle Hidden
    Write-Host "       FastAPI backend process spawned (PID: $($Global:BackendProcess.Id))." -ForegroundColor Gray

    # Wait for Backend to become healthy
    $backendReady = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:$BackendPort/api/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
            if ($health) {
                $backendReady = $true
                break
            }
        } catch {}
    }

    if ($backendReady) {
        Write-Host "       FastAPI Backend is healthy at http://127.0.0.1:$BackendPort [OK]" -ForegroundColor Green
    } else {
        Write-Host "       [WARNING] Backend did not respond to /api/health within 15s. Checking logs..." -ForegroundColor Yellow
    }

    # -------------------------------------------------------------------------
    # Step 4: Launch React 19 / Vite Frontend
    # -------------------------------------------------------------------------
    Write-Host "`n[4/5] Starting React 19 / Vite Frontend on port $FrontendPort..." -ForegroundColor White
    $frontendDir = Join-Path $ProjectRoot "frontend"
    $frontendArgs = "run dev -- --host $HostAddress --port $FrontendPort"
    $Global:FrontendProcess = Start-Process -FilePath $NpmCmd.Source -ArgumentList $frontendArgs -WorkingDirectory $frontendDir -RedirectStandardOutput $feOutLog -RedirectStandardError $feErrLog -PassThru -WindowStyle Hidden
    Write-Host "       React Vite process spawned (PID: $($Global:FrontendProcess.Id))." -ForegroundColor Gray

    # Persist PID lockfile for supervisor and external discovery
    try {
        $lockData = @{
            supervisor_pid = $PID
            backend_pid = $Global:BackendProcess.Id
            frontend_pid = $Global:FrontendProcess.Id
            ollama_owned = (-not $Global:OllamaPreExisting)
            ollama_pid = $(if ($Global:OllamaProcess) { $Global:OllamaProcess.Id } else { $null })
            created_at = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        }
        $lockFile = Join-Path $ProjectRoot ".launcher_pids.json"
        $lockData | ConvertTo-Json | Set-Content -Path $lockFile -Encoding UTF8
    } catch {}

    # Wait for Frontend to become responsive
    $frontendReady = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            $feResp = Invoke-WebRequest -Uri "http://127.0.0.1:$FrontendPort" -Method Head -TimeoutSec 2 -ErrorAction Stop
            if ($feResp.StatusCode -eq 200) {
                $frontendReady = $true
                break
            }
        } catch {}
    }

    if ($frontendReady) {
        Write-Host "       React Frontend is responsive at http://127.0.0.1:$FrontendPort [OK]" -ForegroundColor Green
    } else {
        Write-Host "       Vite server initializing on http://127.0.0.1:$FrontendPort..." -ForegroundColor Gray
    }

    # -------------------------------------------------------------------------
    # Step 5: Network Addresses & Browser Launch
    # -------------------------------------------------------------------------
    Write-Host "`n[5/5] Ready! Access URLs:" -ForegroundColor White
    $wifiIp = "127.0.0.1"
    try {
        $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias '*Wi-Fi*','*Wireless*' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)
        if ($ip) { $wifiIp = $ip }
    } catch {}

    Write-Host "       * Local Web UI:        http://localhost:$FrontendPort" -ForegroundColor Green
    Write-Host "       * Network / Phone UI:  http://${wifiIp}:$FrontendPort" -ForegroundColor Green
    Write-Host "       * FastAPI Backend:     http://${wifiIp}:$BackendPort" -ForegroundColor Green
    Write-Host "       * API Interactive Docs:http://localhost:$BackendPort/docs" -ForegroundColor Green
    Write-Host "       * Ollama Local AI:     $OllamaUrl" -ForegroundColor Green

    if (-not $NoBrowser) {
        Write-Host "`nOpening default browser at http://localhost:$FrontendPort..." -ForegroundColor Cyan
        Start-Process "http://localhost:$FrontendPort"
    }

    Write-Host "`n======================================================================" -ForegroundColor Cyan
    Write-Host "  SochnaSetu AI is running. Press Ctrl+C in this console to shut down.  " -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Cyan

    # Monitor child processes until interrupted
    while ($true) {
        Start-Sleep -Seconds 2
        if ($Global:BackendProcess -and $Global:BackendProcess.HasExited) {
            $beExit = $Global:BackendProcess.ExitCode
            Write-Host "`n[ALERT] Backend process terminated unexpectedly with exit code $beExit." -ForegroundColor Red
            if (Test-Path $beErrLog) {
                $snippet = Get-Content $beErrLog -Tail 15 -ErrorAction SilentlyContinue
                if ($snippet) {
                    Write-Host "--- Backend Error Output ($beErrLog) ---" -ForegroundColor Yellow
                    $snippet | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
                }
            }
            break
        }
        if ($Global:FrontendProcess -and $Global:FrontendProcess.HasExited) {
            $feExit = $Global:FrontendProcess.ExitCode
            Write-Host "`n[ALERT] Frontend process terminated unexpectedly with exit code $feExit." -ForegroundColor Red
            if (Test-Path $feErrLog) {
                $snippet = Get-Content $feErrLog -Tail 15 -ErrorAction SilentlyContinue
                if ($snippet) {
                    Write-Host "--- Frontend Error Output ($feErrLog) ---" -ForegroundColor Yellow
                    $snippet | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
                }
            }
            break
        }
    }
}
catch {
    Write-Host "`n[ERROR] An unhandled exception occurred: $_" -ForegroundColor Red
}
finally {
    Stop-SochnaSetuServices
}
