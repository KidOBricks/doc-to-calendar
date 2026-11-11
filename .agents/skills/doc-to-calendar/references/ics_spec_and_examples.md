# iCalendar (.ics) Reference & Event Formatting Guidelines

## Standard Event Title Formula

Every calendar event title must strictly follow the format:

```text
[SHORT CODE - ]CATEGORY - Event Title
```

### Examples:
- With Course/Context Short Code:
  - `BUS - DEADLINE - Assignment 1: Strategy Memo`
  - `TU/e - HOLIDAY - Carnival Vacation`
  - `CS101 - EXAM - Midterm Exam`
  - `MATH200 - LECTURE - Multivariable Calculus Lecture 1`
  - `BIO - TUTORIAL - Lab Session: Gel Electrophoresis`
  - `RES - MILESTONE - Thesis Proposal Draft Due`
  - `REG - ADMIN - Course Registration Deadline`
- Without Short Code:
  - `DEADLINE - Final Project Submission`
  - `EXAM - Comprehensive Exam`
  - `HOLIDAY - Summer Vacation`

---

## Category Taxonomy & Label Options

Users can choose between full names, shortened codes, or custom labels:

| Standard Category | Shortened Code | Typical Usage | Default Action / Duration |
| :--- | :--- | :--- | :--- |
| `DEADLINE` | `DL` (or `DUE`) | Assignment submissions, paper hand-ins, code repos | Time asked if missing (default 23:59), 0-minute duration |
| `EXAM` | `EXAM` (or `XM`) | Midterms, finals, quizzes, practicals, presentations | Exact slot (e.g. 2–3 hours), explicit start/end |
| `MEETING` | `MTG` | Mentor meetings, coaching sessions, office hours | Scheduled start/end duration |
| `LECTURE` | `LEC` (or `CLASS`)| Regular classes, keynote talks, guest lectures | Scheduled start/end duration |
| `TUTORIAL` | `TUT` (or `LAB`) | Recitations, problem sessions, lab practicals | Scheduled start/end duration |
| `HOLIDAY` | `HOL` (or `BREAK`)| Vacations, bank holidays, campus closures | All-day event (`VALUE=DATE`) |
| `MILESTONE` | `MILE` | Draft reviews, peer feedback windows, group checkpoints | Timed or all-day |
| `ADMIN` | `ADM` | Drop/add deadlines, tuition due, enrollment dates | Timed or all-day |

### Custom Label Examples:
- Full: `PIV2 - DEADLINE - Student Submission: Assignment 1`
- Shortened: `PIV2 - DL - Student Submission: Assignment 1`
- Custom ("You pick"): `PIV2 - DUE - Student Submission: Assignment 1` or `PIV2 - GRADING - Mentor Deadline: Assignment 2`

---

## Event Description Guidelines

Descriptions should be rich and formatted with clear emoji indicators:
- 📌 **Category**: e.g., Assignment / Midterm Exam / Reading Week
- 📝 **Details**: Description of the task, instructions, deliverables
- ⚖️ **Grading Weight**: e.g., 15% of final course grade
- 🔗 **Submission / Links**: Canvas, Gradescope, Portal, or Zoom link
- 📍 **Location**: Room number, lecture hall, or building
- 👤 **Contact**: Professor or TA name / office hours
- 📚 **Readings / Prep**: Chapters, articles, or prerequisites
