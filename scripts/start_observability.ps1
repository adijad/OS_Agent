$ErrorActionPreference = "Continue"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

$ComposeFile = Join-Path `
    $ProjectRoot `
    "docker-compose-observability.yml"

$GrafanaBaseUrl = `
    "http://127.0.0.1:3000"

$GrafanaHealthUrl = `
    "$GrafanaBaseUrl/api/health"

$GrafanaSearchUrl = `
    "$GrafanaBaseUrl/api/search?query=OS_Agent"


Write-Host ""
Write-Host "============================"
Write-Host "OS AGENT OBSERVABILITY"
Write-Host "============================"
Write-Host ""


# ============================================
# CHECK DOCKER
# ============================================

Write-Host "Checking Docker..."

# Run through cmd so Docker warnings written to stderr
# do not become terminating PowerShell error records.
cmd.exe /c "docker info >nul 2>&1"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Docker is not available."
    Write-Host "Please start Docker Desktop."
    exit 1
}

Write-Host "Docker is running."


# ============================================
# START OBSERVABILITY STACK
# ============================================

Write-Host ""
Write-Host "Starting observability stack..."

docker compose `
    -f $ComposeFile `
    up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Failed to start observability stack."
    exit 1
}


# ============================================
# WAIT FOR GRAFANA
# ============================================

Write-Host ""
Write-Host "Waiting for Grafana..."

$GrafanaReady = $false

for ($i = 0; $i -lt 30; $i++) {

    try {
        $Health = Invoke-RestMethod `
            -Uri $GrafanaHealthUrl `
            -TimeoutSec 2 `
            -ErrorAction Stop

        if ($Health) {
            $GrafanaReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $GrafanaReady) {
    Write-Host ""
    Write-Host "Grafana did not become ready."
    exit 1
}

Write-Host "Grafana is ready."


# ============================================
# FIND OS_AGENT DASHBOARD
# ============================================

Write-Host ""
Write-Host "Looking for OS_Agent dashboard..."

try {

    $Dashboards = Invoke-RestMethod `
        -Uri $GrafanaSearchUrl `
        -TimeoutSec 5 `
        -ErrorAction Stop

    $Dashboard = $Dashboards |
        Where-Object {
            $_.type -eq "dash-db" -and
            (
                $_.title -eq "OS_Agent" -or
                $_.title -eq "OS Agent"
            )
        } |
        Select-Object -First 1

    if ($Dashboard) {

        $DashboardUrl = (
            $GrafanaBaseUrl +
            $Dashboard.url
        )

        Write-Host "Opening OS_Agent dashboard..."

        Start-Process $DashboardUrl
    }
    else {

        Write-Host ""
        Write-Host "OS_Agent dashboard was not found."
        Write-Host "Opening Grafana dashboards instead."

        Start-Process `
            "$GrafanaBaseUrl/dashboards"
    }
}
catch {

    Write-Host ""
    Write-Host "Could not query dashboard list."
    Write-Host "Opening Grafana."

    Start-Process `
        $GrafanaBaseUrl
}


Write-Host ""
Write-Host "Observability stack is ready."