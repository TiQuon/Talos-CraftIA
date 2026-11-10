# SPDX-FileCopyrightText: 2026 TiQuon_
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: Copyright 2026 TiQuon_ (https://github.com/TiQuon/Talos-CraftIA)
# Commercial use requires a separate written license from the copyright owner
# (see COMMERCIAL.md). Contributions: see CLA.md.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:Path = "$env:USERPROFILE\.cargo\bin;C:\Users\TiQuon\.local\bin;" + $env:Path

$failed = 0

function Invoke-Step([string]$Name, [scriptblock]$Block) {
    Write-Host "==> $Name"
    try {
        & $Block
        if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
            throw "exit $LASTEXITCODE"
        }
        Write-Host "OK $Name"
    } catch {
        Write-Host "FAIL $Name : $_"
        $script:failed++
    }
}

Invoke-Step "check_headers" { python "$Root\tools\check_headers.py" }
Invoke-Step "check_identity" { python "$Root\tools\check_identity.py" }

if (Get-Command reuse -ErrorAction SilentlyContinue) {
    $tracked = @(git -C $Root ls-files)
    if ($tracked.Count -eq 0) {
        Write-Host "SKIP reuse lint (no tracked git files yet; run after git add)"
    } else {
        Invoke-Step "reuse lint" { reuse lint }
    }
} else {
    Write-Host "SKIP reuse lint (reuse not installed)"
}

if (Test-Path "$Root\core\pyproject.toml") {
    Invoke-Step "ruff" {
        Push-Location "$Root\core"
        uv run ruff check src tests
        Pop-Location
    }
    Invoke-Step "pytest" {
        Push-Location "$Root\core"
        uv run pytest
        Pop-Location
    }
}

if (Test-Path "$Root\engine\Cargo.toml") {
    Invoke-Step "cargo fmt" { cargo fmt --manifest-path "$Root\engine\Cargo.toml" -- --check }
    Invoke-Step "cargo clippy" { cargo clippy --manifest-path "$Root\engine\Cargo.toml" -- -D warnings }
    Invoke-Step "cargo test" { cargo test --manifest-path "$Root\engine\Cargo.toml" }
} else {
    Write-Host "SKIP cargo (engine not scaffolded yet)"
}

if (Get-Command cargo -ErrorAction SilentlyContinue) {
    $deny = cargo --list | Select-String "^\s*deny\b"
    if ($deny) {
        Invoke-Step "cargo deny" { cargo deny check --manifest-path "$Root\engine\Cargo.toml" }
    } else {
        Write-Host "SKIP cargo deny (install MSVC Build Tools, then cargo install cargo-deny)"
    }
}

if ($failed -gt 0) {
    Write-Host "tools/check FAILED ($failed steps)"
    exit 1
}
Write-Host "tools/check PASSED"
exit 0
