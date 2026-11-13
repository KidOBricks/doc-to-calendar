#!/usr/bin/env python3
"""
push_to_gcalendar.py
Pushes staged calendar events (JSON) directly to Google Calendar via the `gcalendar` CLI,
with per-category color IDs (1-11), target calendar resolution, and cross-platform RFC3339 timestamps.
Zero external dependencies (pure Python standard library).
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

# Official Google Calendar Event Colors (ID -> Name & Hex)
GCAL_EVENT_COLORS = {
    "1": ("Lavender", "#a4bdfc"),
    "2": ("Sage", "#7ae7bf"),
    "3": ("Grape", "#dbadff"),
    "4": ("Flamingo", "#ff887c"),
    "5": ("Banana", "#fbd75b"),
    "6": ("Tangerine", "#ffb878"),
    "7": ("Peacock", "#46d6db"),
    "8": ("Graphite", "#e1e1e1"),
    "9": ("Blueberry", "#5484ed"),
    "10": ("Basil", "#51b749"),
    "11": ("Tomato", "#dc2127"),
}

DEFAULT_CATEGORY_COLORS = {
    "DEADLINE": "11",
    "DDL": "11",
    "DL": "11",
    "DUE": "11",
    "EXAM": "4",
    "XM": "4",
    "MILESTONE": "5",
    "MILE": "5",
    "ADMIN": "6",
    "ADM": "6",
    "MEETING": "9",
    "MEET": "9",
    "MTG": "9",
    "LECTURE": "9",
    "LEC": "9",
    "CLASS": "9",
    "TUTORIAL": "7",
    "TUT": "7",
    "LAB": "7",
    "HOLIDAY": "2",
    "HOL": "2",
    "BREAK": "2",
    "FLIGHT": "3",
    "TRAVEL": "3",
    "EVENT": "10",
    "EVT": "10",
}


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> datetime.date:
    """Returns the date of the nth weekday (0=Mon..6=Sun) in a month. n=-1 means last."""
    if n > 0:
        first = datetime.date(year, month, 1)
        offset = (weekday - first.weekday()) % 7
        return first + datetime.timedelta(days=offset + (n - 1) * 7)
    else:
        if month == 12:
            last = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        offset = (last.weekday() - weekday) % 7
        return last - datetime.timedelta(days=offset)


def _fallback_offset_minutes(tzid: str, dt: datetime.datetime) -> int:
    """
    Pure-Python fallback UTC offset (in minutes) when OS lacks IANA tzdata (e.g., Windows without tzdata).
    Covers EU, UK, US/Canada, Australia, and common fixed-offset zones accurately.
    """
    tz = (tzid or "").strip()
    if tz in ("UTC", "Etc/UTC", "GMT", ""):
        return 0

    eu_zones = {
        "Europe/Amsterdam": 60, "Europe/Paris": 60, "Europe/Berlin": 60,
        "Europe/Brussels": 60, "Europe/Madrid": 60, "Europe/Rome": 60,
        "Europe/Vienna": 60, "Europe/Zurich": 60, "Europe/Stockholm": 60,
        "Europe/Oslo": 60, "Europe/Copenhagen": 60, "Europe/Warsaw": 60,
        "Europe/Prague": 60, "Europe/Budapest": 60,
        "Europe/London": 0, "Europe/Dublin": 0, "Europe/Lisbon": 0,
        "Europe/Athens": 120, "Europe/Helsinki": 120, "Europe/Bucharest": 120,
    }
    if tz in eu_zones:
        std_min = eu_zones[tz]
        dst_start = datetime.datetime.combine(
            _nth_weekday_of_month(dt.year, 3, 6, -1), datetime.time(2, 0)
        )
        dst_end = datetime.datetime.combine(
            _nth_weekday_of_month(dt.year, 10, 6, -1), datetime.time(3, 0)
        )
        return std_min + (60 if dst_start <= dt.replace(tzinfo=None) < dst_end else 0)

    us_zones = {
        "America/New_York": -300, "America/Toronto": -300, "America/Detroit": -300,
        "America/Chicago": -360, "America/Winnipeg": -360,
        "America/Denver": -420, "America/Edmonton": -420,
        "America/Los_Angeles": -480, "America/Vancouver": -480,
        "America/Anchorage": -540,
    }
    if tz in us_zones:
        std_min = us_zones[tz]
        dst_start = datetime.datetime.combine(
            _nth_weekday_of_month(dt.year, 3, 6, 2), datetime.time(2, 0)
        )
        dst_end = datetime.datetime.combine(
            _nth_weekday_of_month(dt.year, 11, 6, 1), datetime.time(2, 0)
        )
        return std_min + (60 if dst_start <= dt.replace(tzinfo=None) < dst_end else 0)

    fixed_zones = {
        "Asia/Tokyo": 540, "Asia/Seoul": 540, "Asia/Singapore": 480,
        "Asia/Shanghai": 480, "Asia/Hong_Kong": 480, "Asia/Taipei": 480,
        "Asia/Dubai": 240, "Asia/Kolkata": 330, "America/Phoenix": -420,
        "Pacific/Honolulu": -600, "America/Sao_Paulo": -180,
    }
    if tz in fixed_zones:
        return fixed_zones[tz]

    if tz in ("Australia/Sydney", "Australia/Melbourne"):
        # DST starts 1st Sun Oct, ends 1st Sun Apr
        d_naive = dt.replace(tzinfo=None)
        apr_end = datetime.datetime.combine(_nth_weekday_of_month(dt.year, 4, 6, 1), datetime.time(3, 0))
        oct_start = datetime.datetime.combine(_nth_weekday_of_month(dt.year, 10, 6, 1), datetime.time(2, 0))
        is_dst = d_naive < apr_end or d_naive >= oct_start
        return 600 + (60 if is_dst else 0)

    # Final fallback: use OS local timezone offset for the target date
    local_dt = dt.replace(tzinfo=None).astimezone()
    offset = local_dt.utcoffset()
    return int(offset.total_seconds() // 60) if offset else 0


def to_rfc3339(dt_str: str, tzid: str = "") -> tuple[str, bool]:
    """
    Converts an ISO date/datetime string into (formatted_value, is_all_day).
    - All-day dates ('YYYY-MM-DD') remain 'YYYY-MM-DD'.
    - Timed strings acquire exact RFC3339 offset (e.g. '2026-11-20T23:59:00+01:00').
    """
    s = dt_str.strip()
    if "T" not in s and len(s) == 10:
        datetime.datetime.strptime(s, "%Y-%m-%d")
        return s, True

    # Already has Z or offset?
    if s.endswith("Z"):
        return s, False
    # Check trailing +HH:MM or -HH:MM
    if len(s) >= 6 and s[-6] in ("+", "-") and s[-3] == ":":
        return s, False

    naive = None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
        try:
            naive = datetime.datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    if naive is None:
        naive = datetime.datetime.fromisoformat(s)

    if tzid:
        try:
            import zoneinfo
            zi = zoneinfo.ZoneInfo(tzid)
            aware = naive.replace(tzinfo=zi)
            return aware.isoformat(), False
        except Exception:
            mins = _fallback_offset_minutes(tzid, naive)
            tz_obj = datetime.timezone(datetime.timedelta(minutes=mins))
            return naive.replace(tzinfo=tz_obj).isoformat(), False
    else:
        return naive.astimezone().isoformat(), False


def resolve_color_id(event: dict, color_map: dict) -> str:
    """Resolves the Google Calendar color ID (1-11) for an event from explicit fields or category map."""
    if event.get("color"):
        c = str(event["color"]).strip()
        if c in GCAL_EVENT_COLORS:
            return c

    cat = (event.get("category") or "").strip().upper()
    if cat and cat in color_map and str(color_map[cat]) in GCAL_EVENT_COLORS:
        return str(color_map[cat])

    # Try title prefix match (e.g., 'CS101 - DDL - ...')
    title_upper = (event.get("title") or "").upper()
    for key, val in color_map.items():
        if key.upper() in title_upper.split(" - ") and str(val) in GCAL_EVENT_COLORS:
            return str(val)

    if cat in DEFAULT_CATEGORY_COLORS:
        return DEFAULT_CATEGORY_COLORS[cat]
    for key, val in DEFAULT_CATEGORY_COLORS.items():
        if key in title_upper.split(" - "):
            return val
    return ""


def run_gcalendar(args_list: list[str], account: str = "") -> subprocess.CompletedProcess:
    exe = shutil.which("gcalendar")
    if not exe:
        raise FileNotFoundError(
            "The 'gcalendar' CLI was not found on PATH. Ensure the Google Calendar plugin is installed and initialized."
        )
    env = os.environ.copy()
    if account:
        env["AGY_ACCOUNT"] = account
    return subprocess.run([exe] + args_list, capture_output=True, text=True, env=env, encoding="utf-8")


def resolve_calendar_id(cal_spec: str, account: str = "") -> str:
    """If cal_spec matches an existing calendar's summary name (case-insensitive), return its calendar ID."""
    if not cal_spec or cal_spec == "primary" or "@" in cal_spec:
        return cal_spec or "primary"

    res = run_gcalendar(["readonly", "calendars", "--json"], account=account)
    if res.returncode != 0:
        return cal_spec

    try:
        cals = json.loads(res.stdout)
        target_lower = cal_spec.strip().lower()
        for c in cals:
            if (c.get("summary") or "").strip().lower() == target_lower:
                return c["id"]
            if (c.get("summaryOverride") or "").strip().lower() == target_lower:
                return c["id"]
    except Exception:
        pass
    return cal_spec


def main():
    parser = argparse.ArgumentParser(
        description="Push staged doc-to-calendar JSON events directly to Google Calendar via `gcalendar` CLI."
    )
    parser.add_argument("-i", "--input", help="Path to staged events JSON file. Reads stdin if omitted.")
    parser.add_argument("--cal", default="", help="Target Google Calendar ID or exact Calendar Name (default: primary)")
    parser.add_argument(
        "--color-map",
        default="",
        help='Category to colorId (1-11) mapping as key=val pairs or JSON, e.g. "DDL=11,EXAM=4,LEC=9"',
    )
    parser.add_argument("--account", default="", help="Optional AGY_ACCOUNT email when multiple accounts are connected")
    parser.add_argument("--list-calendars", action="store_true", help="List available Google Calendars as JSON and exit")
    parser.add_argument("--list-colors", action="store_true", help="List Google Calendar event colors as JSON and exit")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print gcalendar commands without creating events")
    args = parser.parse_args()

    if args.list_calendars:
        res = run_gcalendar(["readonly", "calendars", "--json"], account=args.account)
        sys.stdout.write(res.stdout)
        if res.returncode != 0:
            sys.stderr.write(res.stderr)
            sys.exit(res.returncode)
        return

    if args.list_colors:
        res = run_gcalendar(["readonly", "colors", "--json"], account=args.account)
        sys.stdout.write(res.stdout)
        if res.returncode != 0:
            sys.stderr.write(res.stderr)
            sys.exit(res.returncode)
        return

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    tzid = (data.get("timezone") or "").strip()
    events = data.get("events", [])
    if not events:
        print("No events found in input JSON.", file=sys.stderr)
        sys.exit(1)

    name_to_id = {name.lower(): cid for cid, (name, _) in GCAL_EVENT_COLORS.items()}
    name_to_id.update({
        "red": "11", "pink": "4", "coral": "4", "orange": "6", "yellow": "5",
        "mint": "2", "green": "10", "cyan": "7", "teal": "7", "gray": "8",
        "grey": "8", "blue": "9", "purple": "3", "violet": "1",
    })

    def _norm_color(val: str) -> str:
        s = str(val).strip()
        return name_to_id.get(s.lower(), s)

    color_map = {}
    if isinstance(data.get("category_colors"), dict):
        for k, v in data["category_colors"].items():
            color_map[k.strip().upper()] = _norm_color(v)
    if args.color_map:
        raw_cm = args.color_map.strip()
        if raw_cm.startswith("{"):
            cli_map = json.loads(raw_cm)
            for k, v in cli_map.items():
                color_map[k.strip().upper()] = _norm_color(v)
        else:
            for pair in raw_cm.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    color_map[k.strip().upper()] = _norm_color(v)

    raw_cal = args.cal or data.get("google_calendar_id") or data.get("calendar_id") or "primary"
    cal_id = raw_cal if args.dry_run and "@" not in raw_cal and raw_cal != "primary" else None
    if not args.dry_run:
        cal_id = resolve_calendar_id(raw_cal, account=args.account)
    else:
        cal_id = raw_cal

    results = []
    errors = []

    for idx, ev in enumerate(events, 1):
        title = ev.get("title", "Untitled Event")
        start_raw = ev.get("start")
        if not start_raw:
            continue

        start_val, is_all_day = to_rfc3339(start_raw, tzid=tzid)
        end_raw = ev.get("end")

        if is_all_day:
            start_date = datetime.datetime.strptime(start_val, "%Y-%m-%d").date()
            if end_raw:
                end_val_parsed, end_is_date = to_rfc3339(end_raw, tzid=tzid)
                end_date = datetime.datetime.strptime(end_val_parsed[:10], "%Y-%m-%d").date()
                if end_date <= start_date:
                    end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = start_date + datetime.timedelta(days=1)
            end_val = end_date.strftime("%Y-%m-%d")
        else:
            if end_raw:
                end_val, _ = to_rfc3339(end_raw, tzid=tzid)
            else:
                # Default 1 hour duration if no explicit end
                dt_start = datetime.datetime.fromisoformat(start_val)
                end_val = (dt_start + datetime.timedelta(hours=1)).isoformat()

        cmd_args = [
            "mutate", "create",
            "--cal", cal_id,
            "--summary", title,
            "--start", start_val,
            "--end", end_val,
            "--send-updates", "none",
        ]
        if is_all_day:
            cmd_args.append("--all-day")
        if ev.get("location"):
            cmd_args.extend(["--location", ev["location"]])
        if ev.get("description"):
            cmd_args.extend(["--description", ev["description"]])

        color_id = resolve_color_id(ev, color_map)
        if color_id:
            cmd_args.extend(["--color", color_id])

        if args.dry_run:
            results.append({
                "index": idx,
                "title": title,
                "start": start_val,
                "end": end_val,
                "all_day": is_all_day,
                "color": color_id or "default",
                "command": ["gcalendar"] + cmd_args,
            })
        else:
            res = run_gcalendar(cmd_args, account=args.account)
            if res.returncode == 0:
                link = ""
                for line in res.stdout.splitlines():
                    if "Link:" in line or "https://www.google.com/calendar" in line or "https://calendar.google.com" in line:
                        link = line.split("Link:")[-1].strip()
                results.append({
                    "index": idx,
                    "title": title,
                    "color": color_id or "default",
                    "link": link,
                    "raw": res.stdout.strip(),
                })
            else:
                errors.append({
                    "index": idx,
                    "title": title,
                    "error": (res.stderr or res.stdout).strip(),
                })

    output = {
        "calendar_id": cal_id,
        "dry_run": args.dry_run,
        "created_count": len(results),
        "error_count": len(errors),
        "events": results,
        "errors": errors,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
