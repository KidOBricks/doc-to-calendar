---
name: doc-to-calendar
description: >-
  Universal calendar extractor. Extracts events, deadlines, exams, meetings, flights, and
  holidays from documents (PDF, DOCX, TXT, MD, CSV, ICS), images/screenshots (PNG, JPG, WEBP),
  or pasted text/notes. Supports a zero-prompt `quick` mode with optimal auto-settings, interactive
  clarification (scope, cohorts, missing times, alarms, custom category tags, short codes),
  RFC 5545 .ics export, and direct Google Calendar sync with per-category colors and calendar selection.
---

# Universal Doc-to-Calendar Extractor (`doc-to-calendar`)

Use this skill whenever the user attaches a document or image, pastes text/notes, or points to a schedule and wants events extracted into an RFC 5545 `.ics` file and/or pushed directly to **Google Calendar**.

---

## Invocation Modes & Arguments

Check the user's message for mode flags before starting:

### ⚡ Quick Mode (`quick`, `--quick`, `"fast"`, `"auto"`)
If the user invokes `/doc-to-calendar quick` (or includes `--quick`, `quick`, `auto`, `fast` as an argument/intent):
- **SKIP Step 3 (Interactive Clarification) completely.**
- Apply the **Optimal Auto-Settings** immediately:
  - **Scope**: All key events, deadlines, exams, milestones, meetings, flights/travel, and holidays (if multiple tracks/sections appear and none is specified, include shared events and label section variants clearly in titles).
  - **Short Code**: Auto-infer a clean 2–6 character uppercase code if obvious from context (e.g., `CS101`, `LAUNCH`, `TRIP`, `WORK`), otherwise omit.
  - **Category Labels**: Shortened codes (`DDL`, `XM`, `MTG`, `LEC`, `TUT`, `HOL`, `MILE`, `FLIGHT`, `EVT`, `ADM`).
  - **Missing Times**: `23:59` for `DDL` (deadlines) without a time; **All-Day** (`YYYY-MM-DD`) for `HOL`/`EVT`/`FLIGHT` date-only entries without a time; `09:00` (1h) for timed meetings missing hours.
  - **Timezone**: Detect via `gcalendar readonly working-hours --json` (if available), else document timezone, else local OS timezone.
  - **Alarms**: Smart category alarms (`DDL`/`XM`: `-1440, -120`; `MTG`/`LEC`/`TUT`/`EVT`: `-30`; `FLIGHT`: `-180`; `HOL`: `[]`).
  - **Destination**:
    - Default in `quick` mode: Generate the `.ics` file immediately and show the preview table + summary of auto-applied settings.
    - If the user also specified Google Calendar in quick mode (e.g., `/doc-to-calendar quick gcal` or `"quick add to google calendar"`): Push straight to their `primary` calendar (or named calendar if specified) using the **Recommended Google Calendar Color Palette** below!

### 🎛️ Standard Interactive Mode (Default)
Run the full 5-stage workflow with a **single compact clarification step** so the user gets full customization with minimal back-and-forth.

---

## Workflow Overview

```text
1. Ingest Input (Documents / Images & Screenshots / Pasted Text)
        │
        ▼
2. Analyze, Categorize & Stage Candidates
        │
        ▼
3. Interactive Clarification (SKIP if `quick` mode)
        │  └─ Scope, Missing Times, Category Style, Alarms, Short Code,
        │     Destination (.ics vs Google Calendar, Calendar & Colors)
        ▼
4. Preview Table
        │
        ▼
5. Generate .ics &/or Push to Google Calendar with Category Colors
```

---

## Step 1: Ingest Input (All Modalities Supported)

Accept any of the following inputs seamlessly:
1. **Documents**: `.pdf`, `.docx`, `.doc`, `.txt`, `.md`, `.csv`, `.tsv`, `.html`, `.ics`, `.json` — inspect via `read_file` or Python extraction.
2. **Images & Screenshots**: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp` (screenshots of portals/emails, event flyers, Instagram posts, handwritten whiteboards, timetable images) — inspect directly with vision (`read_file` on image path or attached chat image), preserving rows, columns, and color cues.
3. **Pasted Text / Unstructured Notes**: Direct chat text, email threads, Slack/WhatsApp dumps, copied web tables, or bulleted itineraries. No file attachment required.

Inspect carefully across all sections:
- Schedule tables, date headers, multi-line cells
- Deadlines, assessments, grading weights, deliverables
- Travel itineraries, flight numbers, check-in windows
- Holidays, closures, cohorts/tracks, recurring slots, room numbers, and URLs.

---

## Step 2: Analyze & Stage Candidates

Categorize each event into standard categories (adapting naturally to academic, work, travel, or personal contexts):
- `DEADLINE` (`DDL` / `DUE`): Submissions, assignments, deliverables, filings, RSVPs.
- `EXAM` (`XM`): Midterms, finals, quizzes, evaluations, defenses.
- `MEETING` (`MTG`): Work syncs, 1:1s, doctor/client appointments, mentor calls.
- `LECTURE` (`LEC`): Classes, keynotes, talks, webinars.
- `TUTORIAL` (`TUT`): Labs, workshops, recitations, exercise sections.
- `FLIGHT` (`FLIGHT`): Flights, trains, check-in/out, transit legs.
- `MILESTONE` (`MILE`): Checkpoints, launches, reviews, sprints.
- `HOLIDAY` (`HOL`): Vacations, bank holidays, closures, time off.
- `EVENT` (`EVT`): Social events, conferences, parties, general entries.
- `ADMIN` (`ADM`): Registrations, enrollments, billing/admin windows.

Construct rich descriptions where available:
- 📌 **Details / Deliverable**
- ⚖️ **Weight / Priority** (e.g., *Worth 20% of grade*)
- 🔗 **Portal / Meeting Link**
- 📍 **Location / Room**
- 📚 **Prep / Readings / Notes**

---

## Step 3: Interactive Clarification Phase (Skip in `quick` mode)

Before generating output, ask **one compact, well-structured set of questions** (using `ask_question` when helpful, or clear bulleted choices in chat) covering only what is actually ambiguous or needed:

1. **Extraction Scope**: Full schedule vs. Key deadlines/exams/milestones only (or specific category filter).
2. **Cohorts, Tracks & Groups** *(only if detected in input)*: Ask which stream (e.g., Bachelor vs. Master) or lab/tutorial group applies.
3. **Missing Times & All-Day Preference**: For date-only deadlines without an explicit hour, ask preferred time (default `23:59`, e.g., `18:00`, or All-Day).
4. **Category Label Style & Short Code**:
   - Labels: **Shortened** (`DDL`, `XM`, `MTG`, `EVT` — Recommended), **Full** (`DEADLINE`, `EXAM`, `MEETING`), or **Custom** (e.g., `DUE`, `CLASS`).
   - Optional short prefix (e.g., `CS101`, `TRIP`, `WORK`).
5. **Embedded Reminders / Alarms**: Recommend `-P1D` + `-PT2H` for deadlines/exams and `-PT30M` for meetings/sessions (or custom / none).
6. **Timezone & Output Name**: Confirm timezone (auto-detected) and `.ics` filename / calendar name.
7. **Google Calendar Sync & Category Colors**:
   - Ask destination: **Download `.ics` only**, **Add directly to Google Calendar**, or **Both**?
   - If Google Calendar is chosen (or user expressed interest):
     1. Run `python "<skill_dir>/scripts/push_to_gcalendar.py" --list-calendars` to inspect their existing Google Calendars.
     2. Ask **Target Calendar**:
        - Choose an **existing calendar** by name (list their calendars cleanly), **OR**
        - **Create a new calendar**: Give them the 1-click Google Calendar creation link `https://calendar.google.com/calendar/r/settings/createcalendar` (once they create & name it and confirm, re-run `--list-calendars` to fetch its ID and push all events!).
     3. Ask **Color per Category** (list the detected categories and offer the **Recommended Palette** as #1 choice so they can approve in 1 click or customize any category):

| Color ID | Google Calendar Color | Swatch | Recommended Default For |
| :--- | :--- | :--- | :--- |
| `11` | **Tomato** (Red) | `#dc2127` | `DDL` / `DEADLINE` |
| `4` | **Flamingo** (Coral) | `#ff887c` | `EXAM` / `XM` |
| `5` | **Banana** (Yellow) | `#fbd75b` | `MILE` / `MILESTONE` |
| `6` | **Tangerine** (Orange) | `#ffb878` | `ADM` / `ADMIN` |
| `9` | **Blueberry** (Blue) | `#5484ed` | `MTG` / `LEC` |
| `7` | **Peacock** (Teal) | `#46d6db` | `TUT` / `LAB` |
| `2` | **Sage** (Mint) | `#7ae7bf` | `HOL` / `HOLIDAY` |
| `3` | **Grape** (Purple) | `#dbadff` | `FLIGHT` / `TRAVEL` |
| `10` | **Basil** (Green) | `#51b749` | `EVT` / `EVENT` |
| `1` | **Lavender** | `#a4bdfc` | Optional |
| `8` | **Graphite** (Gray) | `#e1e1e1` | Optional |

*(Note: If the `gcalendar` CLI is not available/authenticated in the user's environment, let them know and focus on generating the RFC 5545 `.ics` file plus instructions to install the Google Calendar plugin or import the `.ics`.)*

---

## Step 4: Title Formatting & Staging Preview

Format every event title strictly as:
```text
[SHORT CODE - ]CATEGORY - Event Title
```

Display a clear Markdown preview table before finalizing:
```markdown
| Date | Time | Category | Google Color | Title | Location / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-11-20 | 23:59 | DDL | Tomato (11) | BUS - DDL - Assignment 1 | Canvas • 15% |
```

---

## Step 5: Generate `.ics` and/or Push to Google Calendar

Resolve the skill's `scripts/` directory dynamically (where `SKILL.md` lives, e.g., `~/.codex/skills/doc-to-calendar/scripts/`, `$CODEX_HOME/skills/doc-to-calendar/scripts/`, `~/.gemini/config/plugins/doc-to-calendar/skills/doc-to-calendar/scripts/`, `~/.claude/skills/doc-to-calendar/scripts/`, `~/.cursor/skills/doc-to-calendar/scripts/`, or workspace `.agents/skills/doc-to-calendar/scripts/`).

### 5A. Generate RFC 5545 `.ics` File (With Automatic No-Runner Fallbacks)

1. **Primary (when command runner + Python are available):**
   Run with `python3` (or `python`, or `py -3` on Windows):
```bash
python3 "<skill_dir>/scripts/generate_ics.py" -i "staged_events.json" -o "<chosen_filename>.ics"
```

2. **Fallback 1 (if the local command runner fails to start, shell is disabled, Python is unavailable, or `generate_ics.py` cannot be reached):**
   **NEVER stop or tell the user no `.ics` file could be created.** An `.ics` file is plain UTF-8 text — generate the RFC 5545 `.ics` content yourself and write `<chosen_filename>.ics` directly using your file-writing tool (`write_to_file` / file creation tool), following these RFC 5545 rules (see `references/ics_spec_and_examples.md`):
   - `VCALENDAR` header: `VERSION:2.0`, `PRODID:-//DocToCalendar//Agent//EN`, `CALSCALE:GREGORIAN`, `METHOD:PUBLISH`, `X-WR-CALNAME:<name>`, `X-WR-TIMEZONE:<tz>`.
   - Each `VEVENT`: unique `UID:<uuid>@doctocalendar`, UTC `DTSTAMP:YYYYMMDDTHHMMSSZ`, `SUMMARY`, `DTSTART;TZID=<tz>:YYYYMMDDTHHMMSS` + `DTEND;TZID=<tz>:YYYYMMDDTHHMMSS` (or `DTSTART;VALUE=DATE:YYYYMMDD` + exclusive next-day `DTEND;VALUE=DATE:YYYYMMDD` for all-day), `DESCRIPTION`, `LOCATION`, `CATEGORIES`, `STATUS:CONFIRMED`, `TRANSP:OPAQUE`, and any `VALARM` blocks (`ACTION:DISPLAY`, `TRIGGER:-P1D` / `-PT30M`).
   - Escape `\` → `\\`, `;` → `\;`, `,` → `\,`, newlines → `\n` in text fields, and fold any line over 75 UTF-8 bytes onto the next line with a single leading space.

3. **Fallback 2 (if both the command runner AND file-writing tools fail / are read-only):**
   Output the complete, valid RFC 5545 `.ics` content directly in chat inside a fenced ```` ```ics ```` code block (so the user can save it as `<chosen_filename>.ics`), **plus** clickable `https://calendar.google.com/calendar/render?action=TEMPLATE&text=...&dates=...&ctz=...` quick-add links for each event.

#### Staged JSON Schema:
```json
{
  "calendar_name": "My Schedule",
  "timezone": "Europe/Amsterdam",
  "default_reminders": [-1440, -120],
  "category_colors": {
    "DDL": "11",
    "EXAM": "4",
    "LEC": "9",
    "HOL": "2"
  },
  "events": [
    {
      "title": "BUS - DDL - Assignment 1",
      "start": "2026-11-20T23:59:00",
      "end": "2026-11-20T23:59:00",
      "description": "Submit via Canvas.\nWorth 15% of final grade.",
      "location": "Canvas",
      "category": "DDL",
      "reminders": [-1440, -120]
    },
    {
      "title": "BUS - HOL - Winter Break",
      "start": "2026-12-24",
      "end": "2027-01-08",
      "description": "Closed for holidays.",
      "category": "HOL",
      "reminders": []
    }
  ]
}
```

### 5B. Push Directly to Google Calendar (Optional / User Requested)
1. Ensure the `gcalendar` CLI is initialized (run `<gcalendar_skill>/scripts/gcalendar --version` once if needed, then always invoke bare `gcalendar`).
2. Before writing to an existing calendar, inspect relevant dates with `gcalendar readonly events --cal "<cal_id>" --start ... --end ...` if checking for duplicates or conflicts.
3. Run the bundled Google Calendar pusher script (supports calendar **ID** or exact **Calendar Name**, plus `--color-map` with numeric IDs or color names like `DDL=Tomato,EXAM=4,LEC=Blueberry`):
```bash
python3 "<skill_dir>/scripts/push_to_gcalendar.py" -i "staged_events.json" --cal "<calendar_id_or_name>" --color-map "DDL=11,EXAM=4,LEC=9,HOL=2"
```
*(Add `--dry-run` first if verifying timestamps/colors, or `--account <email>` if multiple accounts are connected.)*

### Final Delivery
- Provide a clickable `file:///` link to any generated `.ics` file (or the ready-to-save ```` ```ics ```` block + Google Calendar quick-add links if file writing was blocked).
- Print every created Google Calendar event's clickable `Link:` URL and confirm target calendar + color assignments.
- Clean up any temporary intermediate JSON files if created in scratch directories unless requested otherwise.
