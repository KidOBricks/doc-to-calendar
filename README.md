<div align="center">

# 📅 doc-to-calendar

**The universal AI agent skill to turn any syllabus, document, or schedule into clean calendar events (`.ics`).**

[![Antigravity](https://img.shields.io/badge/Antigravity-Supported-4285F4?style=flat-square&logo=google)](https://antigravity.google)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Supported-D97706?style=flat-square)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code)
[![Cursor](https://img.shields.io/badge/Cursor-Rules%20Ready-000000?style=flat-square)](https://cursor.com)
[![Codex](https://img.shields.io/badge/OpenAI%20Codex-Ready-10A37F?style=flat-square)](https://openai.com)
[![RFC 5545](https://img.shields.io/badge/iCalendar-RFC%205545%20Compliant-34D399?style=flat-square)](#)
[![Python Standard Library](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python)-blue?style=flat-square)](#)

</div>

---

## ⚡ Overview

**`doc-to-calendar`** is a cross-platform, multi-agent skill that ingests course syllabi, academic calendars, conference schedules, and project timelines in PDF, Word (`.docx`), or Markdown format, guides you through an **interactive clarification phase**, formats events with custom category tags, and outputs an RFC 5545 compliant `.ics` calendar file ready for **Google Calendar**, **Apple Calendar**, or **Outlook**.

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
Clone directly into your project repository:
```bash
git clone https://github.com/KidOBricks/doc-to-calendar.git .agents/skills/doc-to-calendar
```

---

## 🛠️ How It Works

```text
[PDF / DOCX / Markdown Schedule]
               │
               ▼
   1. Document Parsing & Analysis
   (Extract tables, topics, due dates, grading %)
               │
               ▼
   2. Interactive Clarification Questionnaire
   (Scope, tracks/cohorts, tutorial timeslots, alarms, labels)
               │
               ▼
   3. Event Titling & Custom Tagging
   ([SHORT CODE - ]CATEGORY - Event Title)
               │
               ▼
   4. Staging Review Table & RFC 5545 Generator
               │
               ▼
   5. Downloadable .ics Calendar File
```

---

## 💬 Usage

Simply upload your syllabus or document in chat and run:

```text
/doc-to-calendar
```

### The Interactive Clarification Experience

When activated, the agent reads the document and asks targeted questions before scheduling:

1. **Extraction Scope**: Full schedule (all lectures + tutorials + deadlines) vs. deadlines and exams only.
2. **Cohort / Program Selection**: Disambiguates Bachelor vs. Master deadlines, undergraduate tracks, or honors sections.
3. **Tutorial / Lab Timeslot**: Selects your specific recurring group if multiple sections are listed.
4. **Missing Deadline Times**: Asks your preferred time (e.g., `23:59`) for dates without an explicit hour.
5. **Category Labeling**:
   - **Full Names**: `DEADLINE`, `MEETING`, `LECTURE`, `EXAM`
   - **Shortened Codes**: `DDL`, `MEET`, `LEC`, `XM`
   - **You Pick (Custom)**: `DUE`, `CLASS`, `RUBRIC`, etc.
6. **Notification Alerts**: Embedded alarms (e.g. 1 week, 1 day, 15 min before meetings; 6 hours before deadlines).
7. **Short Code**: Optional prefix (e.g. `CS101`, `BUS`, `TU/e`).
8. **Filename**: Output name (e.g. `Bio101_Schedule.ics`).

---

## 🏷️ Title Formatting Formula

```text
[SHORT CODE - ]CATEGORY - Event Title
```

### Examples:
| Style | Example |
| :--- | :--- |
| **Custom Shortened** | `CS101 - DDL - Problem Set 1: Basics & Control Flow` |
| **Meetings** | `PIV2 - MEET - Student Mentor Meeting 1: Vision Recap` |
| **Exams** | `MATH200 - EXAM - Midterm Examination` |
| **Lectures** | `BUS - LEC - Strategy & Organizational Economics` |
| **Holidays** | `TU/e - HOL - Carnival Vacation` |

---

## 🐍 Standalone CLI Usage (Zero Agent Needed)

You can also use the generator directly in CI/CD, scripts, or the terminal:

```bash
# Print .ics directly to stdout
python scripts/generate_ics.py -i examples/sample_syllabus_input.json

# Save to file
python scripts/generate_ics.py -i examples/sample_syllabus_input.json -o my_schedule.ics
```

### Input JSON Schema:
```json
{
  "calendar_name": "CS101 Intro to Computer Science",
  "timezone": "America/New_York",
  "default_reminders": [-1440, -120],
  "events": [
    {
      "title": "CS101 - DDL - Problem Set 1",
      "start": "2026-09-18T23:59:00",
      "end": "2026-09-18T23:59:00",
      "category": "DDL",
      "location": "Gradescope",
      "description": "Submit via Gradescope.\nWorth 10% of grade.",
      "reminders": [-1440, -120]
    }
  ]
}
```

---

## 📁 Repository Structure

```text
doc-to-calendar/
├── .agents/skills/doc-to-calendar/    # Antigravity project skill mirror
├── .claude/skills/doc-to-calendar/    # Claude Code project skill mirror
├── .cursor/rules/doc-to-calendar.mdc  # Cursor IDE rule
├── scripts/
│   └── generate_ics.py                # Pure standard library RFC 5545 generator
├── references/
│   └── ics_spec_and_examples.md       # Category standards & format reference
├── examples/
│   ├── sample_syllabus_input.json     # Example staged JSON
│   └── sample_output.ics              # Example generated calendar file
├── install.sh                         # 1-line installer (macOS / Linux)
├── install.ps1                        # 1-line installer (Windows)
├── SKILL.md                           # Universal agent skill specification
├── plugin.json                        # Antigravity / Claude plugin manifest
└── README.md                          # Documentation
```

---

## 🤝 Contributing

Contributions, feature requests, and improvements are welcome! Feel free to open an issue or pull request at [https://github.com/KidOBricks/doc-to-calendar](https://github.com/KidOBricks/doc-to-calendar).
