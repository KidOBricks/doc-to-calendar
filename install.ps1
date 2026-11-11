#
# doc-to-calendar Universal Multi-Agent Installer (Windows PowerShell)
# Installs doc-to-calendar for Antigravity, Claude Code, and Codex.
#

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstalledCount = 0

Write-Host "Installing doc-to-calendar across AI coding agents..." -ForegroundColor Cyan

# 1. Google Antigravity
$AgyPluginDir = Join-Path $HOME ".gemini\config\plugins\doc-to-calendar"
New-Item -ItemType Directory -Force -Path (Join-Path $HOME ".gemini\config\plugins") | Out-Null
if (Test-Path $AgyPluginDir) { Remove-Item -Recurse -Force $AgyPluginDir }
New-Item -ItemType Directory -Force -Path (Join-Path $AgyPluginDir "skills") | Out-Null
Copy-Item "$ScriptDir\plugin.json", "$ScriptDir\README.md" -Destination $AgyPluginDir -Force
Copy-Item -Recurse "$ScriptDir" -Destination (Join-Path $AgyPluginDir "skills\doc-to-calendar") -Force
Write-Host "  Installed for Google Antigravity ($AgyPluginDir)" -ForegroundColor Green
$InstalledCount++

# 2. Claude Code
$ClaudeSkillDir = Join-Path $HOME ".claude\skills\doc-to-calendar"
New-Item -ItemType Directory -Force -Path (Join-Path $HOME ".claude\skills") | Out-Null
if (Test-Path $ClaudeSkillDir) { Remove-Item -Recurse -Force $ClaudeSkillDir }
Copy-Item -Recurse "$ScriptDir" -Destination $ClaudeSkillDir -Force
Write-Host "  Installed for Claude Code ($ClaudeSkillDir)" -ForegroundColor Green
$InstalledCount++

# 3. OpenAI Codex
$CodexDir = Join-Path $HOME ".codex"
if (Test-Path $CodexDir) {
    $CodexSkillDir = Join-Path $CodexDir "skills\doc-to-calendar"
    New-Item -ItemType Directory -Force -Path (Join-Path $CodexDir "skills") | Out-Null
    if (Test-Path $CodexSkillDir) { Remove-Item -Recurse -Force $CodexSkillDir }
    Copy-Item -Recurse "$ScriptDir" -Destination $CodexSkillDir -Force
    Write-Host "  Installed for Codex ($CodexSkillDir)" -ForegroundColor Green
    $InstalledCount++
}

Write-Host ""
Write-Host "Successfully installed doc-to-calendar for $InstalledCount agent environments!" -ForegroundColor Yellow
Write-Host "Type /doc-to-calendar in chat with any syllabus, PDF, or schedule." -ForegroundColor Cyan
