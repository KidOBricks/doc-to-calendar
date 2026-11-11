---
name: doc-to-calendar
description: >-
  Extracts events, deadlines, exams, lectures, and holidays from uploaded documents (PDF, DOCX,
  academic syllabi, course schedules, project roadmaps), conducts interactive clarification
  (cohorts, missing times, alarms, short codes), formats titles with standard tags
  ('[SHORT CODE - ]CATEGORY - Event Title'), and generates an RFC 5545 compliant .ics file
  for Google Calendar and calendar apps.
---

# Document-to-Calendar Extractor (`doc-to-calendar`)

Use this skill whenever the user uploads or points to a document (such as a course syllabus, university calendar, academic schedule, conference itinerary, or project timeline in PDF, Word, or text format) and requests to extract deadlines, exams, sessions, or events into a downloadable calendar file (`.ics`).

---

## Workflow Overview

Follow this 5-stage workflow strictly:

```
1. Ingest & Parse Document
        │
        ▼
2. Analyze & Stage Candidates
        │
        ▼
3. Interactive Clarification Phase (Ask User)
        │
        ▼
4. Event Staging Preview Table
        │
        ▼
5. Generate .ics & Deliver Download Link
```

---

## Step 1: Ingest & Parse Document

1. Read the document using `read_file` or relevant file inspection tools.
2. Carefully inspect all sections:
   - **Weekly schedule tables** (maps week numbers, lecture dates, assignment due dates).
   - **Grading & Assessment breakdown** (percentages, deliverable descriptions).
   - **Academic calendar / Key dates** (term start, drop/add, holidays, reading weeks, finals).
   - **Administrative details** (locations, room numbers, online links, office hours).

---

## Step 2: Analyze & Stage Candidates

Identify each prospective calendar entry and categorize it into one of the standard categories:
- `DEADLINE`: Assignment submissions, problem sets, projects, essay deadlines.
- `EXAM`: Midterms, final exams, quizzes, practicals, presentations.
- `LECTURE`: Regular class sessions, guest lectures, course meetings.
- `TUTORIAL`: Recitations, lab practicals, exercise sessions, workshops.
- `HOLIDAY`: Breaks, vacations, university closures, bank holidays.
- `MILESTONE`: Proposal draft hand-in, peer review window, checkpoints.
- `ADMIN`: Course add/drop deadlines, registration windows, tuition deadlines.

For each event, construct a **rich description**:
- **Deliverable / Topic**: Exactly what is due or covered.
- **Grading Weight**: e.g., *"Worth 20% of final grade"*.
- **Submission Portal**: e.g., Canvas, Gradescope, email, portal link.
- **Location**: Building/room number or virtual meeting link.
- **Required Prep**: Relevant chapters, reading assignments.

---

## Step 3: Interactive Clarification Phase (Required)

Before generating the final `.ics` file, **ask the user targeted questions** using `ask_question` or direct chat to resolve ambiguities:

1. **Extraction Scope**:
   - Ask whether they want the **full schedule** (lectures + tutorials + deadlines) or **deadlines, exams, milestones, and holidays only**.
2. **Cohorts & Tracks Disambiguation**:
   - If the document contains Bachelor vs. Master streams, undergraduate vs. graduate deadlines, or separate tracks/electives, ask which applies to them.
3. **Tutorial / Lab Timeslot Selection**:
   - If the syllabus lists multiple recurring lab/tutorial groups (e.g., *Group A on Tuesdays vs. Group B on Thursdays*), ask which section they are enrolled in.
4. **Missing Deadline Times**:
   - For any deadline where the document specifies a date without an exact hour (or says "midnight"), ask what time they want it set to (e.g., `23:59`).
5. **Category Labels Customization**:
   - Explicitly list the detected categories in the document (e.g., *"I found the following categories: DEADLINE, MEETING, LECTURE"*).
   - Ask how the user would like these category labels displayed in the event titles:
     1. **Full Category Names** (e.g., `DEADLINE`, `MEETING`, `LECTURE`, `EXAM`)
     2. **Shortened Codes** (e.g., `DL`, `MTG`, `LEC`, `XM`)
     3. **Custom Labels (You pick)**: Allow the user to specify custom labels for any or all categories (e.g., `DUE` instead of `DEADLINE`, `CLASS` instead of `LECTURE`, `RUBRIC` for grading deadlines).
6. **Reminders & Alarms Preference**:
   - Ask what notification alerts they prefer embedded in the `.ics` (e.g., *1 day before + 2 hours before for deadlines*, *15 minutes before classes*, or *none*).
7. **Course / Context Short Code**:
   - Ask if they would like an optional short prefix prepended to all event titles (e.g., `BUS` for Business, `TU/e` for University-wide, `CS101`, `PIV2`).
8. **Output Filename**:
   - Ask what they want the output `.ics` file to be named (e.g., `CourseName_Deadlines.ics`).
9. **Timezone Confirmation**:
   - If the document specifies a different timezone or doesn't mention one, confirm the appropriate timezone (e.g., `Europe/Amsterdam`).

---

## Step 4: Title Formatting & Preview

### Event Title Formula
Format every event title as:
```text
[SHORT CODE - ]CATEGORY - Event Title
```

*Examples with short code*:
- `BUS - DEADLINE - Assignment 1: Memo`
- `TU/e - HOLIDAY - Spring Vacation`
- `CS101 - EXAM - Midterm Exam`
- `MATH - LECTURE - Linear Algebra Lecture 1`

*Examples without short code*:
- `DEADLINE - Final Project Submission`
- `EXAM - Final Exam`
- `HOLIDAY - Summer Break`

### Preview Table
Present a clear Markdown table for the user:
```markdown
| Date | Time | Category | Title | Location / Key Details |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-20 | 23:59 | DEADLINE | BUS - DEADLINE - Assignment 1 | Canvas • 15% grade |
| 2026-12-05 | 09:00 - 12:00 | EXAM | BUS - EXAM - Midterm Exam | Aud 3 • Closed book |
```

---

## Step 5: Generate the RFC 5545 `.ics` File

Use the bundled generator script to output a 100% compliant `.ics` file:

```powershell
python "C:\Users\20230928\.gemini\config\skills\doc-to-calendar\scripts\generate_ics.py" -i "staged_events.json" -o "<chosen_filename>.ics"
```

Or pass the JSON payload directly via stdin:
```powershell
$jsonPayload | python "C:\Users\20230928\.gemini\config\skills\doc-to-calendar\scripts\generate_ics.py" -o "<chosen_filename>.ics"
```

### JSON Structure for the Generator:
```json
{
  "calendar_name": "Course Schedule",
  "timezone": "Europe/Amsterdam",
  "default_reminders": [-1440, -120],
  "events": [
    {
      "title": "BUS - DEADLINE - Assignment 1",
      "start": "2026-11-20T23:59:00",
      "end": "2026-11-20T23:59:00",
      "description": "Submit via Canvas.\nWorth 15% of final grade.\nReadings: Chapter 3 & 4.",
      "location": "Canvas",
      "category": "DEADLINE",
      "reminders": [-1440, -120]
    },
    {
      "title": "TU/e - HOLIDAY - Winter Break",
      "start": "2026-12-24",
      "end": "2027-01-08",
      "description": "University campus closed.",
      "category": "HOLIDAY",
      "reminders": []
    }
  ]
}
```

### Final Delivery
Provide the user with a clickable `file://` link to the generated `.ics` file:
```markdown
Your calendar file has been created:
👉 [Download <filename>.ics](file:///<absolute-path-to-file>)

You can double-click this file on your computer or import it into Google Calendar via **Settings > Import & export**.
```
