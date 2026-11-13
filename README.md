<div align="center">

# 📅 doc-to-calendar

**The universal AI agent skill & web app to turn any document, screenshot, or pasted notes into `.ics` calendars or directly into Google Calendar.**

[![Antigravity](https://img.shields.io/badge/Antigravity-Supported-4285F4?style=flat-square&logo=google)](https://antigravity.google)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Supported-D97706?style=flat-square)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code)
[![Cursor](https://img.shields.io/badge/Cursor-Rules%20Ready-000000?style=flat-square)](https://cursor.com)
[![Codex](https://img.shields.io/badge/OpenAI%20Codex-Ready-10A37F?style=flat-square)](https://openai.com)
[![RFC 5545](https://img.shields.io/badge/iCalendar-RFC%205545%20Compliant-34D399?style=flat-square)](#)
[![Python Standard Library](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python)-blue?style=flat-square)](#)

</div>

---

## ⚡ Overview

**`doc-to-calendar`** is a cross-platform, multi-agent skill and web tool that ingests **documents** (PDF, `.docx`, Markdown, TXT, CSV, HTML, `.ics`), **images & screenshots** (PNG, JPG, WEBP, flyers, whiteboards), and **pasted text/notes** (emails, chat dumps, itineraries).

Choose between **zero-friction `quick` mode** (auto best settings) or **interactive customization** with category tagging (`[SHORT CODE - ]CATEGORY - Event Title`), embedded alarms, RFC 5545 `.ics` export, and **direct Google Calendar sync with per-category colors and existing/new calendar selection**.

🌐 **Live Web App**: [https://kidobricks.github.io/doc-to-calendar/](https://kidobricks.github.io/doc-to-calendar/)

---

## 🚀 Quick Install (Pick Your Agent)

### Option 1: Universal 1-Line Installer

#### macOS / Linux
```bash
curl -fsSL https://raw.githubusercontent.com/KidOBricks/doc-to-calendar/main/install.sh | bash
```

#### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/KidOBricks/doc-to-calendar/main/install.ps1 | iex
```

---

### Option 2: Manual Clone by Agent

#### Google Antigravity
```bash
git clone https://github.com/KidOBricks/doc-to-calendar.git ~/.gemini/config/plugins/doc-to-calendar
```

#### Claude Code
```bash
git clone https://github.com/KidOBricks/doc-to-calendar.git ~/.claude/skills/doc-to-calendar
```

#### Cursor / Project-Scoped (Any Workspace)
```bash
git clone https://github.com/KidOBricks/doc-to-calendar.git .agents/skills/doc-to-calendar
```

---

## 💬 Usage

### Standard Mode (Full Customization)
Attach a PDF, Word doc, screenshot/photo, or paste text directly in chat and run:
```text
/doc-to-calendar
```

### ⚡ Quick Mode (`quick` / `--quick`)
Skip all questions and let the skill automatically apply optimal defaults (all key events, shortened category tags, `23:59` for date-only deadlines, all-day for date-only holidays/events, smart per-category alarms, auto-detected timezone) and generate `.ics` immediately:
```text
/doc-to-calendar quick
```
*(Want it pushed straight to Google Calendar in one step? Run `/doc-to-calendar quick gcal`.)*

---

## 🗓️ Google Calendar Direct Sync & Category Colors

When using Antigravity with the `gcalendar` plugin (or OAuth sync in the web app), **`doc-to-calendar`** can:
1. **Pick Target Calendar**: Add events into any **existing calendar** on your Google account OR guide/create a **brand-new calendar**.
2. **Color-Code per Category**: Assign any of the 11 official Google Calendar colors to each detected category (e.g., `DDL` → Tomato Red `11`, `EXAM` → Flamingo `4`, `LEC`/`MEET` → Blueberry `9`, `HOL` → Sage `2`, `FLIGHT` → Grape `3`, `MILE` → Banana `5`, `EVT` → Basil `10`).

---

## 🏷️ Title Formatting Formula

```text
[SHORT CODE - ]CATEGORY - Event Title
```

| Style | Example |
| :--- | :--- |
| **Deadlines** | `CS101 - DDL - Problem Set 1: Basics & Control Flow` |
| **Meetings** | `PIV2 - MEET - Mentor Sync 1: Vision Recap` |
| **Exams** | `MATH200 - XM - Midterm Examination` |
| **Flights / Travel** | `TRIP - FLIGHT - AMS -> JFK (KL0641)` |
| **Holidays** | `TU/e - HOL - Carnival Vacation` |

---

## 🐍 Standalone CLI Usage (Zero Agent Needed)

### Generate RFC 5545 `.ics`
```bash
python scripts/generate_ics.py -i examples/sample_syllabus_input.json -o my_schedule.ics
```

### Push Directly to Google Calendar (with Category Colors)
```bash
# List your available Google Calendars
python scripts/push_to_gcalendar.py --list-calendars

# Push events to an existing calendar by name or ID with per-category colors
python scripts/push_to_gcalendar.py -i examples/sample_syllabus_input.json \
  --cal "primary" \
  --color-map "DDL=11,EXAM=4,LEC=9,HOL=2"
```

---

## 📁 Repository Structure

```text
doc-to-calendar/
├── .agents/skills/doc-to-calendar/    # Universal project skill mirror
├── .claude/skills/doc-to-calendar/    # Claude Code skill mirror
├── .cursor/rules/doc-to-calendar.mdc  # Cursor IDE rule
├── scripts/
│   ├── generate_ics.py                # Pure Python RFC 5545 .ics generator
│   └── push_to_gcalendar.py           # Pure Python Google Calendar batch sync (with colors)
├── references/
│   └── ics_spec_and_examples.md       # Category standards & format reference
├── examples/
│   └── sample_syllabus_input.json     # Example staged JSON
├── index.html                         # Standalone Zyfn-branded Web App
├── http-functions.js                  # Wix Velo Gemini 3.8 Flash High backend
├── install.sh                         # 1-line installer (macOS / Linux)
├── install.ps1                        # 1-line installer (Windows)
├── SKILL.md                           # Universal agent skill specification
├── plugin.json                        # Antigravity / Claude plugin manifest
└── README.md                          # Documentation
```

---

## 🤝 Contributing

Contributions, feature requests, and improvements are welcome at [https://github.com/KidOBricks/doc-to-calendar](https://github.com/KidOBricks/doc-to-calendar).
