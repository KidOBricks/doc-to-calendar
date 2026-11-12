#
# doc-to-calendar Universal Multi-Agent Installer (Windows PowerShell)
# Supports both:
# 1) One-line web install: irm https://raw.githubusercontent.com/KidOBricks/doc-to-calendar/main/install.ps1 | iex
# 2) Local install: .\install.ps1
#

$ErrorActionPreference = "Stop"
Write-Host ""
Write-Host "📅 Installing doc-to-calendar across AI coding agents..." -ForegroundColor Cyan

$TempDir = $null
$NeedsCleanup = $false

# Determine source directory
if ($MyInvocation.MyCommand -and $MyInvocation.MyCommand.Path) {
    $SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    # Running via web pipe (irm | iex) -> Download latest repository zip from GitHub
    Write-Host "  📦 Fetching latest release from GitHub..." -ForegroundColor Gray
    $TempZip = Join-Path ([System.IO.Path]::GetTempPath()) ("doc-to-calendar-" + [System.Guid]::NewGuid().ToString().Substring(0,8) + ".zip")
    $TempExtract = Join-Path ([System.IO.Path]::GetTempPath()) ("doc-to-calendar-" + [System.Guid]::NewGuid().ToString().Substring(0,8))
    
    Invoke-WebRequest -Uri "https://github.com/KidOBricks/doc-to-calendar/archive/refs/heads/main.zip" -OutFile $TempZip -UseBasicParsing
    Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
    Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
    
    $SourceDir = Join-Path $TempExtract "doc-to-calendar-main"
    $TempDir = $TempExtract
    $NeedsCleanup = $true
}

$InstalledCount = 0

try {
    # 1. Google Antigravity Plugin (~/.gemini/config/plugins/doc-to-calendar)
    $AgyPluginDir = Join-Path $HOME ".gemini\config\plugins\doc-to-calendar"
    $AgySkillDir = Join-Path $AgyPluginDir "skills\doc-to-calendar"
    New-Item -ItemType Directory -Force -Path $AgySkillDir | Out-Null
    
    if (Test-Path (Join-Path $SourceDir "plugin.json")) { Copy-Item (Join-Path $SourceDir "plugin.json") -Destination $AgyPluginDir -Force }
    if (Test-Path (Join-Path $SourceDir "README.md")) { Copy-Item (Join-Path $SourceDir "README.md") -Destination $AgyPluginDir -Force }
    Copy-Item -Path "$SourceDir\*" -Destination $AgySkillDir -Recurse -Force
    Write-Host "  ✅ Installed for Google Antigravity ($AgyPluginDir)" -ForegroundColor Green
    $InstalledCount++

    # 2. Claude Code Skill (~/.claude/skills/doc-to-calendar)
    $ClaudeSkillDir = Join-Path $HOME ".claude\skills\doc-to-calendar"
    New-Item -ItemType Directory -Force -Path $ClaudeSkillDir | Out-Null
    Copy-Item -Path "$SourceDir\*" -Destination $ClaudeSkillDir -Recurse -Force
    Write-Host "  ✅ Installed for Claude Code ($ClaudeSkillDir)" -ForegroundColor Green
    $InstalledCount++

    # 3. OpenAI Codex (~/.codex/skills/doc-to-calendar)
    $CodexSkillDir = Join-Path $HOME ".codex\skills\doc-to-calendar"
    New-Item -ItemType Directory -Force -Path $CodexSkillDir | Out-Null
    Copy-Item -Path "$SourceDir\*" -Destination $CodexSkillDir -Recurse -Force
    Write-Host "  ✅ Installed for OpenAI Codex ($CodexSkillDir)" -ForegroundColor Green
    $InstalledCount++

    # 4. Universal Agents Standard (~/.agents/skills/doc-to-calendar)
    $AgentsSkillDir = Join-Path $HOME ".agents\skills\doc-to-calendar"
    New-Item -ItemType Directory -Force -Path $AgentsSkillDir | Out-Null
    Copy-Item -Path "$SourceDir\*" -Destination $AgentsSkillDir -Recurse -Force
    Write-Host "  ✅ Installed for Universal AI Agents ($AgentsSkillDir)" -ForegroundColor Green
    $InstalledCount++

    # 5. Cursor (~/.cursor/skills/doc-to-calendar)
    $CursorSkillDir = Join-Path $HOME ".cursor\skills\doc-to-calendar"
    New-Item -ItemType Directory -Force -Path $CursorSkillDir | Out-Null
    Copy-Item -Path "$SourceDir\*" -Destination $CursorSkillDir -Recurse -Force
    Write-Host "  ✅ Installed for Cursor ($CursorSkillDir)" -ForegroundColor Green
    $InstalledCount++

} finally {
    if ($NeedsCleanup -and $TempDir -and (Test-Path $TempDir)) {
        Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "🎉 Successfully installed doc-to-calendar across $InstalledCount agent environments!" -ForegroundColor Yellow
Write-Host "👉 In your chat, type /doc-to-calendar and attach any document or syllabus." -ForegroundColor Cyan
Write-Host ""
