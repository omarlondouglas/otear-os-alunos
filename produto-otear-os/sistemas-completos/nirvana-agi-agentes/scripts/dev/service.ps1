param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "down", "restart", "logs", "status", "health", "build", "shell")]
    [string]$Action = "status",

    [Parameter(Position = 1)]
    [string]$Service = "all"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

$ComposeServices = @("gateway", "redis", "carousel", "remotion", "chatgpt-bridge")
$LocalServices = @("frontend")
$ServiceGroups = @("video-backend", "video-editor", "social-media")
$VideoBackendServices = @("redis", "remotion", "gateway")
$SocialMediaServices = @("redis", "gateway")
$AllServices = $ComposeServices + $LocalServices + $ServiceGroups

$HealthUrls = @{
    gateway = "http://localhost:8000/health"
    redis = ""
    carousel = "http://localhost:8002/health"
    remotion = "http://localhost:8003/health"
    "chatgpt-bridge" = "http://localhost:10531/health"
    frontend = "http://localhost:5173"
}

function Assert-ServiceName {
    param([string]$Name)
    if ($Name -eq "all") { return }
    if ($AllServices -notcontains $Name) {
        throw "Unknown service '$Name'. Use: all, $($AllServices -join ', ')"
    }
}

function Invoke-Compose {
    param([string[]]$Args)
    Assert-Docker
    & docker compose @Args
}

function Assert-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker CLI was not found in PATH. Install Docker Desktop or use the local/manual commands in docs/guides/SERVICE_COMMANDS.md."
    }
}

function Start-Frontend {
    Push-Location "frontend-react"
    try {
        npm run dev
    }
    finally {
        Pop-Location
    }
}

function Test-Health {
    param([string]$Name)

    if ($Name -eq "redis") {
        Invoke-Compose @("exec", "-T", "redis", "redis-cli", "ping")
        return
    }

    $url = $HealthUrls[$Name]
    if (-not $url) {
        Write-Host "No health URL configured for $Name"
        return
    }

    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        Write-Host "$Name OK $($response.StatusCode) $url"
    }
    catch {
        Write-Host "$Name FAIL $url"
        throw
    }
}

Assert-ServiceName $Service

switch ($Action) {
    "up" {
        if ($Service -eq "all") {
            Invoke-Compose @("up", "-d")
            Write-Host "Docker services started. Start frontend separately with: .\scripts\dev\service.ps1 up frontend"
        }
        elseif ($Service -eq "video-backend" -or $Service -eq "video-editor") {
            Invoke-Compose @("up", "-d", "redis", "remotion")
            Invoke-Compose @("up", "-d", "--no-deps", "gateway")
            Write-Host "Video editor backend started: redis, remotion, gateway. Carousel and frontend were not started."
        }
        elseif ($Service -eq "social-media") {
            Invoke-Compose @("up", "-d", "redis")
            Invoke-Compose @("up", "-d", "--no-deps", "gateway")
            Write-Host "Social media backend started: redis, gateway. Frontend, carousel, remotion, and chatgpt-bridge were not started."
        }
        elseif ($Service -eq "frontend") {
            Start-Frontend
        }
        else {
            Invoke-Compose @("up", "-d", $Service)
        }
    }

    "down" {
        if ($Service -eq "all") {
            Invoke-Compose @("down")
        }
        elseif ($Service -eq "video-backend" -or $Service -eq "video-editor") {
            Invoke-Compose @("stop", "gateway", "remotion", "redis")
        }
        elseif ($Service -eq "social-media") {
            Invoke-Compose @("stop", "gateway", "redis")
        }
        elseif ($ComposeServices -contains $Service) {
            Invoke-Compose @("stop", $Service)
        }
        else {
            Write-Host "Stop the frontend dev server with Ctrl+C in its terminal."
        }
    }

    "restart" {
        if ($Service -eq "all") {
            Invoke-Compose @("restart")
        }
        elseif ($Service -eq "video-backend" -or $Service -eq "video-editor") {
            Invoke-Compose @("restart", "redis", "remotion", "gateway")
        }
        elseif ($Service -eq "social-media") {
            Invoke-Compose @("restart", "redis", "gateway")
        }
        elseif ($ComposeServices -contains $Service) {
            Invoke-Compose @("restart", $Service)
        }
        else {
            Write-Host "Restart frontend by stopping Ctrl+C and running: .\scripts\dev\service.ps1 up frontend"
        }
    }

    "logs" {
        if ($Service -eq "all") {
            Invoke-Compose @("logs", "-f", "--tail", "200")
        }
        elseif ($Service -eq "video-backend" -or $Service -eq "video-editor") {
            Invoke-Compose @("logs", "-f", "--tail", "200", "gateway", "remotion", "redis")
        }
        elseif ($Service -eq "social-media") {
            Invoke-Compose @("logs", "-f", "--tail", "200", "gateway", "redis")
        }
        elseif ($ComposeServices -contains $Service) {
            Invoke-Compose @("logs", "-f", "--tail", "200", $Service)
        }
        else {
            Write-Host "Frontend logs are in the terminal running npm run dev."
        }
    }

    "status" {
        if (Get-Command docker -ErrorAction SilentlyContinue) {
            Invoke-Compose @("ps")
            Write-Host ""
        }
        else {
            Write-Host "Docker CLI was not found in PATH. Docker service status is unavailable."
            Write-Host ""
        }
        Write-Host "Local frontend: run .\scripts\dev\service.ps1 up frontend"
    }

    "health" {
        if ($Service -eq "all") {
            foreach ($name in $ComposeServices) {
                Test-Health $name
            }
            Write-Host "Frontend health only works while Vite is running: $($HealthUrls['frontend'])"
        }
        elseif ($Service -eq "video-backend" -or $Service -eq "video-editor") {
            foreach ($name in $VideoBackendServices) {
                Test-Health $name
            }
        }
        elseif ($Service -eq "social-media") {
            foreach ($name in $SocialMediaServices) {
                Test-Health $name
            }
        }
        else {
            Test-Health $Service
        }
    }

    "build" {
        if ($Service -eq "all") {
            Invoke-Compose @("build")
        }
        elseif ($Service -eq "video-backend" -or $Service -eq "video-editor") {
            Invoke-Compose @("build", "gateway", "remotion")
        }
        elseif ($Service -eq "social-media") {
            Invoke-Compose @("build", "gateway")
        }
        elseif ($ComposeServices -contains $Service) {
            Invoke-Compose @("build", $Service)
        }
        elseif ($Service -eq "frontend") {
            Push-Location "frontend-react"
            try {
                npm run build
            }
            finally {
                Pop-Location
            }
        }
    }

    "shell" {
        if ($Service -eq "all" -or $Service -eq "frontend" -or $Service -eq "video-backend" -or $Service -eq "video-editor" -or $Service -eq "social-media") {
            throw "Shell is only available for Docker services: $($ComposeServices -join ', ')"
        }
        Invoke-Compose @("exec", $Service, "sh")
    }
}
