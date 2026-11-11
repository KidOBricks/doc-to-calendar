#!/usr/bin/env bash
#
# doc-to-calendar Universal Multi-Agent Installer (macOS / Linux)
# Installs doc-to-calendar for Antigravity, Claude Code, and Codex.
#

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLED=0

echo "🚀 Installing doc-to-calendar across AI coding agents..."

# 1. Google Antigravity
ANTIGRAVITY_DIR="$HOME/.gemini/config/plugins/doc-to-calendar"
mkdir -p "$HOME/.gemini/config/plugins"
rm -rf "$ANTIGRAVITY_DIR"
mkdir -p "$ANTIGRAVITY_DIR/skills"
cp -r "$REPO_DIR/plugin.json" "$REPO_DIR/README.md" "$ANTIGRAVITY_DIR/"
cp -r "$REPO_DIR" "$ANTIGRAVITY_DIR/skills/doc-to-calendar"
echo "  ✅ Installed for Google Antigravity ($ANTIGRAVITY_DIR)"
INSTALLED=$((INSTALLED + 1))

# 2. Claude Code
CLAUDE_DIR="$HOME/.claude/skills/doc-to-calendar"
mkdir -p "$HOME/.claude/skills"
rm -rf "$CLAUDE_DIR"
cp -r "$REPO_DIR" "$CLAUDE_DIR"
echo "  ✅ Installed for Claude Code ($CLAUDE_DIR)"
INSTALLED=$((INSTALLED + 1))

# 3. OpenAI Codex
if [ -d "$HOME/.codex" ] || [ -f "$HOME/.codex/config.toml" ]; then
  CODEX_DIR="$HOME/.codex/skills/doc-to-calendar"
  mkdir -p "$HOME/.codex/skills"
  rm -rf "$CODEX_DIR"
  cp -r "$REPO_DIR" "$CODEX_DIR"
  echo "  ✅ Installed for Codex ($CODEX_DIR)"
  INSTALLED=$((INSTALLED + 1))
fi

echo ""
echo "🎉 Successfully installed doc-to-calendar for $INSTALLED agent environments!"
echo "👉 Type /doc-to-calendar in chat with any syllabus, PDF, or schedule."
