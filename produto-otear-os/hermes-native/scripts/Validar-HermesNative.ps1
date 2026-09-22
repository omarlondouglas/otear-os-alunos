[CmdletBinding()]
param(
    [string]$VaultPath
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$checks = 0
$drivePrefix = 'D' + ':'
$forwardSlash = [string][char]47
$backSlash = [string][char]92
$forbiddenPaths = @(
    ($drivePrefix + $forwardSlash + 'SSD 2'),
    ('{' + 'OTEAR_'),
    ($drivePrefix + $forwardSlash + 'Otear/otear-os'),
    ($drivePrefix + $backSlash + 'SSD 2'),
    ($drivePrefix + $backSlash + 'Otear' + $backSlash + 'otear-os')
)

if ([string]::IsNullOrWhiteSpace($VaultPath)) {
    # O script mora em produto-otear-os/hermes-native/scripts. Quatro níveis acima
    # está a raiz portátil da vault, independentemente de onde ela foi baixada.
    $VaultPath = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath)))
}

try {
    $vault = (Resolve-Path -LiteralPath $VaultPath).Path
    $package = Join-Path $vault 'produto-otear-os\hermes-native'
    $scripts = Join-Path $package 'scripts'
    $routeMapPath = Join-Path $package 'route-skill-map.json'
    $routerPath = Join-Path $vault 'produto-otear-os\nucleo-otear\roteador-otear.yaml'
    $baseSkills = @('otear-router', 'otear-skill-creator', 'otear-agent-creator', 'otear-squad-orchestrator')
    $routeMap = Get-Content -Raw -LiteralPath $routeMapPath | ConvertFrom-Json
    $systemSkills = @($routeMap.routes | ForEach-Object { $_.skill } | Sort-Object -Unique)
    $supportSkills = @($routeMap.support_capabilities | ForEach-Object { $_.skill } | Sort-Object -Unique)
    $skills = @($baseSkills + $systemSkills + $supportSkills | Sort-Object -Unique)
    foreach ($required in @($package, $routeMapPath, $routerPath, (Join-Path $package 'README.md'), (Join-Path $scripts 'Instalar-HermesNative.ps1'), (Join-Path $scripts 'Validar-HermesNative.ps1'))) {
        $checks++
        if (-not (Test-Path -LiteralPath $required)) { $failures.Add("Item obrigatorio ausente: $required") }
    }
    foreach ($skill in $skills) {
        $checks++
        $file = Join-Path (Join-Path $package "skills\$skill") 'SKILL.md'
        if (-not (Test-Path -LiteralPath $file)) { $failures.Add("Skill ausente: $skill"); continue }
        $content = Get-Content -Raw -LiteralPath $file
        if (-not $content.StartsWith("---")) { $failures.Add("$skill nao inicia com frontmatter YAML") }
        foreach ($field in @('name:', 'description:', 'version:', 'author:', 'platforms:', 'tools:')) {
            $checks++
            if ($content -notmatch [regex]::Escape($field)) { $failures.Add("$skill nao declara $field") }
        }
        foreach ($forbidden in $forbiddenPaths) {
            $checks++
            if ($content -like "*$forbidden*") { $failures.Add("$skill contem caminho legado: $forbidden") }
        }
    }
    $checks++
    if ($supportSkills.Count -ne 9) {
        $failures.Add("Quantidade inesperada de capacidades complementares: $($supportSkills.Count); esperadas 9.")
    }
    $checks++
    if ($skills.Count -ne 31) {
        $failures.Add("Quantidade inesperada de skills Hermes-native: $($skills.Count); esperadas 31.")
    }
    $routerContent = Get-Content -Raw -LiteralPath $routerPath
    foreach ($route in $routeMap.routes) {
        $checks++
        $routePattern = '(?ms)^  - capacidade:.*?^    otear: "' + [regex]::Escape($route.route) + '".*?^    skill_hermes_native: "' + [regex]::Escape($route.skill) + '"'
        if ($routerContent -notmatch $routePattern) {
            $failures.Add("Rota sem mapeamento Hermes-native correto: $($route.route) -> $($route.skill)")
        }
    }
    foreach ($file in Get-ChildItem -LiteralPath $package -Recurse -File) {
        $checks++
        $content = Get-Content -Raw -LiteralPath $file.FullName
        foreach ($forbidden in $forbiddenPaths) {
            if ($content -like "*$forbidden*") { $failures.Add("Caminho legado em $($file.FullName): $forbidden") }
        }
    }
} catch {
    $failures.Add("Erro no verificador: $($_.Exception.Message)")
}

if ($failures.Count -gt 0) {
    Write-Host "FALHOU: $($failures.Count) problema(s) em $checks verificacoes." -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
    exit 1
}

Write-Host "OK: $checks verificacoes Hermes-native passaram para $vault." -ForegroundColor Green
