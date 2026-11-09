<#
.SYNOPSIS
  Installs Team Kuro (plugins, skills, team roster) into the Antigravity config directory.

.DESCRIPTION
  Safe by default:
    * validates the repository first (python scripts/validate.py) when Python is available
    * backs up whatever it is about to replace into <target>\.kuro-backup\<timestamp>
    * NEVER overwrites config.json, hooks.json or mcp_config.json (your machine-specific settings);
      it only creates them when missing
    * removes known legacy paths from earlier Kuro versions
    * verifies the result and exits non-zero on failure

.PARAMETER TargetDir
  Destination config directory. Default: $HOME\.gemini\config

.PARAMETER EnableInterceptor
  Registers the token-saver PreInvocation prompt interceptor in hooks.json (merged, existing hooks kept).

.PARAMETER DryRun
  Shows what would happen without changing anything.

.PARAMETER SkipValidation
  Skip the repository validation step.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun
#>
[CmdletBinding()]
param(
    [string]$TargetDir = (Join-Path $HOME ".gemini\config"),
    [switch]$EnableInterceptor,
    [switch]$DryRun,
    [switch]$SkipValidation
)

$ErrorActionPreference = "Stop"
$repo = $PSScriptRoot

function Info($m) { Write-Host $m -ForegroundColor Cyan }
function Ok($m)   { Write-Host "  [ok]   $m" -ForegroundColor Green }
function Note($m) { Write-Host "  [note] $m" -ForegroundColor Yellow }
function Act($m)  { if ($DryRun) { Write-Host "  [dry]  $m" -ForegroundColor DarkGray } else { Write-Host "  [do]   $m" } }
function Fail($m) { Write-Host "  [FAIL] $m" -ForegroundColor Red; exit 1 }

Info "=========================================="
Info "  Team Kuro installer"
Info "  source: $repo"
Info "  target: $TargetDir"
if ($DryRun) { Info "  mode  : DRY RUN (no changes)" }
Info "=========================================="

# 1. Validate the repository -------------------------------------------------
if (-not $SkipValidation) {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
    if ($py) {
        Info "`n[1/6] Validating repository"
        & $py.Source (Join-Path $repo "scripts\validate.py")
        if ($LASTEXITCODE -ne 0) { Fail "Repository validation failed (use -SkipValidation to bypass)." }
        Ok "validation passed"
    } else {
        Note "Python not found - skipping validation"
    }
}

# 2. Prepare target ----------------------------------------------------------
Info "`n[2/6] Preparing target"
if (-not (Test-Path $TargetDir)) {
    Act "create $TargetDir"
    if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null }
}

# 3. Backup what we are about to replace -------------------------------------
Info "`n[3/6] Backing up existing managed folders"
$managed = @("plugins", "skills", "team")
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $TargetDir ".kuro-backup"
$backupDir = Join-Path $backupRoot $stamp
$needBackup = $managed | Where-Object { Test-Path (Join-Path $TargetDir $_) }
if ($needBackup) {
    Act "backup $($needBackup -join ', ') -> $backupDir"
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
        foreach ($d in $needBackup) { Copy-Item -Recurse -Force (Join-Path $TargetDir $d) $backupDir }
        # keep only the 3 most recent backups
        Get-ChildItem $backupRoot -Directory | Sort-Object Name -Descending | Select-Object -Skip 3 |
            Remove-Item -Recurse -Force
    }
} else {
    Ok "nothing to back up"
}

# 4. Deploy -------------------------------------------------------------------
Info "`n[4/6] Deploying"
# Legacy paths from earlier Kuro versions (duplicates of the token-saver skill)
$legacy = @("plugins\token-optimization\skills", "skills\token-optimization")
foreach ($l in $legacy) {
    $p = Join-Path $TargetDir $l
    if (Test-Path $p) { Act "remove legacy $l"; if (-not $DryRun) { Remove-Item -Recurse -Force $p } }
}
foreach ($d in $managed) {
    Act "copy $d\"
    if (-not $DryRun) {
        $dest = Join-Path $TargetDir $d
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item -Recurse -Force (Join-Path $repo "$d\*") $dest
    }
}

# 5. Machine-specific config: create-if-missing only --------------------------
Info "`n[5/6] Base configuration (never overwritten)"
$cfgSrc = @{
    "config.json"     = "config.example.json"
    "hooks.json"      = "hooks.json"
    "mcp_config.json" = "mcp_config.json"
}
foreach ($k in $cfgSrc.Keys) {
    $dest = Join-Path $TargetDir $k
    if (Test-Path $dest) { Ok "$k exists - left untouched" }
    else {
        Act "create $k"
        if (-not $DryRun) { Copy-Item -Force (Join-Path $repo $cfgSrc[$k]) $dest }
    }
}

if ($EnableInterceptor) {
    $hookScript = Join-Path $TargetDir "skills\token-saver\resources\intercept_wasteful_prompts.py"
    $hooksFile = Join-Path $TargetDir "hooks.json"
    Act "register PreInvocation interceptor in hooks.json"
    if (-not $DryRun) {
        $raw = if (Test-Path $hooksFile) { Get-Content $hooksFile -Raw } else { "{}" }
        if ([string]::IsNullOrWhiteSpace($raw)) { $raw = "{}" }
        $hooks = $raw | ConvertFrom-Json
        $entry = [pscustomobject]@{
            PreInvocation = @([pscustomobject]@{
                type = "command"
                command = "python `"$($hookScript -replace '\\','/')`""
                timeout = 10
            })
        }
        if ($hooks.PSObject.Properties.Name -contains "kuro-token-guard") { $hooks."kuro-token-guard" = $entry }
        else { $hooks | Add-Member -NotePropertyName "kuro-token-guard" -NotePropertyValue $entry }
        Copy-Item -Force $hooksFile "$hooksFile.bak" -ErrorAction SilentlyContinue
        $hooks | ConvertTo-Json -Depth 10 | Set-Content -Path $hooksFile -Encoding UTF8
        Ok "interceptor registered (previous hooks.json saved as hooks.json.bak)"
    }
}

# 6. Verify -------------------------------------------------------------------
Info "`n[6/6] Verifying"
if ($DryRun) {
    Ok "dry run complete - nothing was changed"
    exit 0
}
$expected = (Get-ChildItem (Join-Path $repo "skills") -Directory).Count
$missing = @()
foreach ($d in Get-ChildItem (Join-Path $repo "skills") -Directory) {
    if (-not (Test-Path (Join-Path $TargetDir "skills\$($d.Name)\SKILL.md"))) { $missing += $d.Name }
}
if ($missing.Count -gt 0) { Fail "missing skills in target: $($missing -join ', ')" }
Ok "$expected skills installed"
foreach ($p in Get-ChildItem (Join-Path $repo "plugins") -Directory) {
    if (-not (Test-Path (Join-Path $TargetDir "plugins\$($p.Name)\plugin.json"))) { Fail "plugin $($p.Name) not installed" }
    Ok "plugin $($p.Name)"
}
if (-not (Test-Path (Join-Path $TargetDir "team\roster.json"))) { Fail "team roster missing" }
Ok "team roster"

$agy = Get-Command agy -ErrorAction SilentlyContinue
if ($agy) {
    & $agy.Source plugins list
    if ($LASTEXITCODE -ne 0) { Note "'agy plugins list' returned $LASTEXITCODE - check your agy installation" }
    else { Ok "agy sees the plugins" }
} else {
    Note "agy not found in PATH - install Antigravity, then run: agy plugins list"
}

Write-Host "`nTeam Kuro installed. Restart agy to load the new rules." -ForegroundColor Green
if ($needBackup) { Write-Host "Backup of previous state: $backupDir" -ForegroundColor DarkGray }
