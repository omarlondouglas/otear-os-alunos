[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$HermesHome,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $PSCommandPath
$packageRoot = Split-Path -Parent $scriptRoot
$sourceSkills = Join-Path $packageRoot 'skills'

if (-not (Test-Path -LiteralPath $sourceSkills -PathType Container)) {
    throw 'Pacote Hermes-native invalido: pasta skills ausente.'
}

$expectedSkills = @(Get-ChildItem -LiteralPath $sourceSkills -Directory | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf
} | Select-Object -ExpandProperty Name | Sort-Object)

if ($expectedSkills.Count -lt 31) {
    throw "Pacote Hermes-native invalido: esperadas ao menos 31 skills; encontradas $($expectedSkills.Count)."
}

$resolvedHome = [System.IO.Path]::GetFullPath($HermesHome)
$targetSkills = Join-Path $resolvedHome 'skills'
$targetNamespace = Join-Path $targetSkills 'otear-os'

foreach ($skill in $expectedSkills) {
    $skillFile = Join-Path (Join-Path $sourceSkills $skill) 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
        throw "Pacote Hermes-native invalido: skill ausente: $skill"
    }
}

if (Test-Path -LiteralPath $targetNamespace) {
    if (-not $Force) {
        throw "Ja existe uma instalacao em $targetNamespace. Use -Force para substituir somente esta pasta."
    }
    Remove-Item -LiteralPath $targetNamespace -Recurse -Force
}

New-Item -ItemType Directory -Path $targetNamespace -Force | Out-Null
foreach ($skill in $expectedSkills) {
    Copy-Item -LiteralPath (Join-Path $sourceSkills $skill) -Destination $targetNamespace -Recurse -Force
}

Write-Host "OK: $($expectedSkills.Count) skills Otear instaladas em $targetNamespace" -ForegroundColor Green
