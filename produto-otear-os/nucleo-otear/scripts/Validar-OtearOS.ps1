[CmdletBinding()]
param(
    [string]$VaultPath
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$checks = 0

if ([string]::IsNullOrWhiteSpace($VaultPath)) {
    $scriptDirectory = Split-Path -Parent $PSCommandPath
    $VaultPath = Join-Path $scriptDirectory "..\..\.."
}

function Test-OtearPath {
    param([string]$RelativePath, [string]$Source)
    $script:checks++
    if ([string]::IsNullOrWhiteSpace($RelativePath)) { return }
    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        $script:failures.Add("$Source usa caminho absoluto: $RelativePath")
        return
    }
    $candidate = Join-Path $VaultPath $RelativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $candidate)) {
        $script:failures.Add("$Source aponta para item ausente: $RelativePath")
    }
}

try {
    $resolvedVault = (Resolve-Path -LiteralPath $VaultPath).Path
    $VaultPath = $resolvedVault
    $catalogPath = Join-Path $VaultPath 'produto-otear-os\catalogo-integracao.json'
    $routerPath = Join-Path $VaultPath 'produto-otear-os\nucleo-otear\roteador-otear.yaml'
    foreach ($required in @('SOUL.md', 'MAPA DO OTEAR OS.md', '.system\USER.md', '.system\MEMORY.md', $catalogPath, $routerPath)) {
        $checks++
        if ([System.IO.Path]::IsPathRooted($required)) {
            $requiredPath = $required
        } else {
            $requiredPath = Join-Path $VaultPath $required
        }
        if (-not (Test-Path -LiteralPath $requiredPath)) {
            $failures.Add("Arquivo obrigatório ausente: $required")
        }
    }

    $catalog = Get-Content -Raw -LiteralPath $catalogPath | ConvertFrom-Json
    foreach ($entry in $catalog.read_order) { Test-OtearPath -RelativePath $entry -Source 'catalogo.read_order' }
    foreach ($component in $catalog.components) {
        Test-OtearPath -RelativePath $component.path -Source "catalogo.$($component.id).path"
        foreach ($path in @($component.related_paths)) { Test-OtearPath -RelativePath $path -Source "catalogo.$($component.id).related_paths" }
    }

    $routerLines = Get-Content -LiteralPath $routerPath
    foreach ($line in $routerLines) {
        if ($line -match '^\s*(principal|apoio|workflow):\s*["'']?([^"''#\r\n]+)') {
            $value = $Matches[2].Trim()
            if ($value -and $value -notmatch '^\[') { Test-OtearPath -RelativePath ("produto-otear-os/" + $value) -Source "roteador.$($Matches[1])" }
        }
        if ($line -match '^\s*-\s*["'']?([^"''#\r\n]+)') {
            $value = $Matches[1].Trim()
            if ($value -match '^((?:skills-base|agentes-base|squads-base|sistemas-completos|sistemas-prontos)/[^:\s]+):') {
                $value = $Matches[1]
            }
            if ($value -match '^(skills-base|agentes-base|squads-base|sistemas-completos|sistemas-prontos)/') { Test-OtearPath -RelativePath ("produto-otear-os/" + $value) -Source 'roteador.lista' }
        }
    }
} catch {
    $failures.Add("Erro ao ler a configuração: $($_.Exception.Message)")
}

if ($failures.Count -gt 0) {
    Write-Host "FALHOU: $($failures.Count) problema(s) encontrado(s) em $checks verificações." -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
    exit 1
}

Write-Host "OK: $checks verificações internas passaram para $VaultPath." -ForegroundColor Green
