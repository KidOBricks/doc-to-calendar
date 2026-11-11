# Doc to Calendar Plugin

An Antigravity plugin for extracting events, deadlines, exams, lectures, and milestones from uploaded documents (PDF, Word, or Markdown) and exporting them into standard RFC 5545 `.ics` calendar files.

## Features

- **Multi-Format Ingestion**: Works with academic syllabi, course guides, exam timetables, and project plans in PDF, DOCX, or text format.
- **Interactive Disambiguation**: Pauses to ask clarifying questions about student cohorts (e.g. Bachelor vs. Master), lab/tutorial timeslots, missing deadline times, and reminder alert preferences.
- **Custom Category Labels**: Choose between full category names (e.g., `DEADLINE`, `MEETING`), shortened abbreviations (`DDL`, `MEET`, `LEC`), or your own custom labels.
- **Rich Event Descriptions**: Captures grading weights, submission portals (Canvas, Gradescope), room locations, instructor contacts, and required readings.
- **RFC 5545 Compliant `.ics` Export**: Clean line folding, timezone tags, and embedded calendar notification alerts (`VALARM`).

## Usage

Type the slash command in chat:

```text
/doc-to-calendar
```

along with your uploaded document or schedule.

## Event Title Formula

```text
[SHORT CODE - ]CATEGORY - Event Title
```

### Examples:
- `PIV2 - DDL - Student Submission: Assignment 1`
- `PIV2 - MEET - Preparation Meeting 1`
- `BUS - DEADLINE - Strategy Memo Submission`
- `TU/e - HOLIDAY - Spring Vacation`

## Installation for Others

To share this plugin with a colleague or friend, have them copy the `doc-to-calendar` directory into their Antigravity plugins directory:

- **Windows**: `%USERPROFILE%\.gemini\config\plugins\doc-to-calendar\`
- **macOS / Linux**: `~/.gemini/config/plugins/doc-to-calendar/`

Or place it inside any shared Git repository under `<repo_root>/.agents/plugins/doc-to-calendar/`.
