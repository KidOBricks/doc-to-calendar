#!/usr/bin/env bash
#
# doc-to-calendar Universal Multi-Agent Installer (macOS / Linux)
# Supports:
# 1) One-line web install: curl -fsSL https://raw.githubusercontent.com/KidOBricks/doc-to-calendar/main/install.sh | bash
# 2) Local install: ./install.sh
#

set -e

echo ""
echo "📅 Installing doc-to-calendar across AI coding agents..."

CLEANUP=0
TEMP_DIR=""

# Check if running locally or via curl | bash
if [ -n "${BASH_SOURCE[0]}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  echo "  📦 Fetching latest release from GitHub..."
  TEMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'doc-to-calendar')"
  CLEANUP=1
  curl -fsSL "https://github.com/KidOBricks/doc-to-calendar/archive/refs/heads/main.tar.gz" | tar -xz -C "$TEMP_DIR"
  SOURCE_DIR="$TEMP_DIR/doc-to-calendar-main"
fi

cleanup() {
  if [ "$CLEANUP" -eq 1 ] && [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
  fi
}
trap cleanup EXIT

INSTALLED=0

# 1. Google Antigravity Plugin (~/.gemini/config/plugins/doc-to-calendar)
AGY_PLUGIN_DIR="$HOME/.gemini/config/plugins/doc-to-calendar"
AGY_SKILL_DIR="$AGY_PLUGIN_DIR/skills/doc-to-calendar"
mkdir -p "$AGY_SKILL_DIR"
if [ -f "$SOURCE_DIR/plugin.json" ]; then cp "$SOURCE_DIR/plugin.json" "$AGY_PLUGIN_DIR/"; fi
if [ -f "$SOURCE_DIR/README.md" ]; then cp "$SOURCE_DIR/README.md" "$AGY_PLUGIN_DIR/"; fi
cp -r "$SOURCE_DIR/"* "$AGY_SKILL_DIR/"
echo "  ✅ Installed for Google Antigravity ($AGY_PLUGIN_DIR)"
INSTALLED=$((INSTALLED + 1))

# 2. Claude Code Skill (~/.claude/skills/doc-to-calendar)
CLAUDE_DIR="$HOME/.claude/skills/doc-to-calendar"
mkdir -p "$CLAUDE_DIR"
cp -r "$SOURCE_DIR/"* "$CLAUDE_DIR/"
echo "  ✅ Installed for Claude Code ($CLAUDE_DIR)"
INSTALLED=$((INSTALLED + 1))

# 3. OpenAI Codex (~/.codex/skills/doc-to-calendar)
CODEX_DIR="$HOME/.codex/skills/doc-to-calendar"
mkdir -p "$CODEX_DIR"
cp -r "$SOURCE_DIR/"* "$CODEX_DIR/"
echo "  ✅ Installed for OpenAI Codex ($CODEX_DIR)"
INSTALLED=$((INSTALLED + 1))

# 4. Universal Agents Standard (~/.agents/skills/doc-to-calendar)
AGENTS_DIR="$HOME/.agents/skills/doc-to-calendar"
mkdir -p "$AGENTS_DIR"
cp -r "$SOURCE_DIR/"* "$AGENTS_DIR/"
echo "  ✅ Installed for Universal AI Agents ($AGENTS_DIR)"
INSTALLED=$((INSTALLED + 1))

# 5. Cursor (~/.cursor/skills/doc-to-calendar)
CURSOR_DIR="$HOME/.cursor/skills/doc-to-calendar"
mkdir -p "$CURSOR_DIR"
cp -r "$SOURCE_DIR/"* "$CURSOR_DIR/"
echo "  ✅ Installed for Cursor ($CURSOR_DIR)"
INSTALLED=$((INSTALLED + 1))

echo ""
echo "🎉 Successfully installed doc-to-calendar across $INSTALLED agent environments!"
echo "👉 In your agent chat, type /doc-to-calendar and attach any document or syllabus."
echo ""
