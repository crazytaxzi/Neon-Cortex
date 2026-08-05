[CmdletBinding()]
param(
    [string]$RepoPath = "",
    [string]$InstallRoot = "$env:LOCALAPPDATA\Neon_Cortex"
)

$ErrorActionPreference = "Stop"
if (-not $RepoPath) {
    $RepoPath = Read-Host "Full path to your Neon-Cortex clone"
}
$RepoPath = (Resolve-Path $RepoPath).Path
if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
    throw "That path is not a Git repository: $RepoPath"
}

$venv = Join-Path $InstallRoot ".venv"
$configDir = Join-Path $InstallRoot "config"
$secretDir = Join-Path $InstallRoot "secrets"
New-Item -ItemType Directory -Force -Path $InstallRoot, $configDir, $secretDir | Out-Null

if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
    py -3 -m venv $venv
}
$python = Join-Path $venv "Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -e $RepoPath

$configSource = Join-Path $RepoPath "config\swarm.bootstrap.json"
$configTarget = Join-Path $configDir "swarm.json"
if (-not (Test-Path $configTarget)) {
    (Get-Content $configSource -Raw).Replace("%LOCALAPPDATA%", ($env:LOCALAPPDATA -replace '\\','/')) |
        Set-Content -Encoding UTF8 $configTarget
}

$tokenFile = Join-Path $secretDir "github-token.txt"
if (-not (Test-Path $tokenFile)) {
    $secure = Read-Host "Fine-grained GitHub token for crazytaxzi/Neon-Cortex" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    Set-Content -NoNewline -Encoding ASCII $tokenFile $token
    $acl = Get-Acl $tokenFile
    $acl.SetAccessRuleProtection($true, $false)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
    $acl.SetAccessRule($rule)
    Set-Acl $tokenFile $acl
}

$runner = Join-Path $InstallRoot "Start-NeonRelay.cmd"
@"
@echo off
setlocal
set "NEON_WORKSPACE=$RepoPath"
"$python" -m neon_relay --config "$configTarget" watch-github
pause
"@ | Set-Content -Encoding ASCII $runner

& $python -m neon_relay --config $configTarget check

Write-Host ""
Write-Host "Neon Relay installed with the existing-model bootstrap profile." -ForegroundColor Green
Write-Host "Workspace alias: %NEON_WORKSPACE% -> $RepoPath"
Write-Host "Configuration: $configTarget"
Write-Host "Start it here: $runner"
Write-Host "The relay processes open GitHub issues whose titles begin with [NEON TASK]."
Write-Host "Qwen is expected at http://127.0.0.1:8081 and GPT-OSS escalation at http://127.0.0.1:8082."
