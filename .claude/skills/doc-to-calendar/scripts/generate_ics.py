#!/usr/bin/env python3
"""
generate_ics.py
Generates RFC 5545 compliant iCalendar (.ics) files from structured JSON data.
Zero external dependencies (pure Python standard library).
"""

import sys
import os
import json
import uuid
import datetime
import argparse

def rfc5545_fold_line(line: str, max_octets: int = 75) -> str:
    """
    Folds a line so that no folded line exceeds max_octets (default 75) in UTF-8 bytes.
    Subsequent lines start with a single space.
    """
    encoded = line.encode('utf-8')
    if len(encoded) <= max_octets:
        return line

    chunks = []
    # First line can be up to max_octets
    current_max = max_octets
    start = 0
    while start < len(encoded):
        end = min(start + current_max, len(encoded))
        # Ensure we don't split in the middle of a multi-byte UTF-8 character
        while end > start and (encoded[end:end+1] != b'' and (encoded[end] & 0xC0) == 0x80):
            end -= 1
        
        chunk = encoded[start:end].decode('utf-8')
        if not chunks:
            chunks.append(chunk)
            current_max = max_octets - 1  # 1 byte reserved for leading space
        else:
            chunks.append(" " + chunk)
        start = end

    return "\r\n".join(chunks)

def escape_text(text: str) -> str:
    r"""
    Escapes special characters in text values per RFC 5545 section 3.3.11.
    Backslash (\) -> \\
    Semicolon (;) -> \;
    Comma (,) -> \,
    Newline (\n or \r\n) -> \n
    """
    if not text:
        return ""
    text = text.replace('\\', '\\\\')
    text = text.replace(';', '\\;')
    text = text.replace(',', '\\,')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.replace('\n', '\\n')
    return text

def format_iso_duration(minutes: int) -> str:
    """
    Converts minutes to an RFC 5545 trigger duration string (e.g. -PT15M, -P1D, -PT2H).
    """
    is_neg = minutes < 0
    abs_m = abs(minutes)
    
    days = abs_m // 1440
    rem = abs_m % 1440
    hours = rem // 60
    mins = rem % 60
    
    res = "-P" if is_neg else "P"
    time_part = ""
    if days > 0:
        res += f"{days}D"
    if hours > 0:
        time_part += f"{hours}H"
    if mins > 0:
        time_part += f"{mins}M"
    if time_part:
        res += "T" + time_part
    if res in ("P", "-P"):
        res += "T0M"
    return res

def parse_iso_datetime(dt_str: str):
    """
    Parses ISO strings like '2026-11-20', '2026-11-20T23:59:00', or with offsets.
    Returns (datetime_obj, is_date_only)
    """
    dt_str = dt_str.strip()
    if 'T' not in dt_str and len(dt_str) == 10:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d").date()
        return dt, True
    
    # Try parsing full ISO datetime
    # Replace trailing Z if present
    dt_clean = dt_str.replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(dt_clean)
        return dt, False
    except ValueError:
        # Fallback to manual formats
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
            try:
                dt = datetime.datetime.strptime(dt_str, fmt)
                return dt, False
            except ValueError:
                pass
        raise ValueError(f"Unable to parse datetime: {dt_str}")

def build_valarm(trigger_minutes: int, action: str = "DISPLAY", description: str = "Reminder") -> list:
    """
    Builds a VALARM component.
    """
    duration_str = format_iso_duration(trigger_minutes)
    lines = [
        "BEGIN:VALARM",
        f"ACTION:{action}",
        f"DESCRIPTION:{escape_text(description)}",
        f"TRIGGER:{duration_str}",
        "END:VALARM"
    ]
    return lines

def generate_ics(data: dict) -> str:
    """
    Generates a full iCalendar string from a dictionary of event data.
    """
    cal_name = data.get("calendar_name", "Extracted Schedule")
    tzid = data.get("timezone", "").strip()
    global_reminders = data.get("default_reminders", [])
    
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//DocToCalendar//Antigravity Agent//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_text(cal_name)}"
    ]
    if tzid:
        lines.append(f"X-WR-TIMEZONE:{tzid}")

    now_utc_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for ev in data.get("events", []):
        lines.append("BEGIN:VEVENT")
        
        # UID
        ev_uid = ev.get("uid") or f"{uuid.uuid4()}@doctocalendar"
        lines.append(f"UID:{ev_uid}")
        lines.append(f"DTSTAMP:{now_utc_str}")

        title = ev.get("title", "Untitled Event")
        lines.append(f"SUMMARY:{escape_text(title)}")

        # Start and End Times
        start_val = ev.get("start")
        if not start_val:
            continue
        
        start_dt, start_is_date = parse_iso_datetime(start_val)
        
        end_val = ev.get("end")
        if end_val:
            end_dt, end_is_date = parse_iso_datetime(end_val)
        else:
            if start_is_date:
                # All day event end is next day in RFC 5545
                end_dt = start_dt + datetime.timedelta(days=1)
                end_is_date = True
            else:
                # Default 1 hour duration
                end_dt = start_dt + datetime.timedelta(hours=1)
                end_is_date = False

        if start_is_date:
            if end_dt <= start_dt:
                end_dt = start_dt + datetime.timedelta(days=1)
            lines.append(f"DTSTART;VALUE=DATE:{start_dt.strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{end_dt.strftime('%Y%m%d')}")
        else:
            if tzid:
                lines.append(f"DTSTART;TZID={tzid}:{start_dt.strftime('%Y%m%dT%H%M%S')}")
                lines.append(f"DTEND;TZID={tzid}:{end_dt.strftime('%Y%m%dT%H%M%S')}")
            else:
                lines.append(f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}")
                lines.append(f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}")

        # Description
        desc = ev.get("description", "")
        if desc:
            lines.append(f"DESCRIPTION:{escape_text(desc)}")

        # Location
        loc = ev.get("location", "")
        if loc:
            lines.append(f"LOCATION:{escape_text(loc)}")

        # Categories
        cat = ev.get("category", "")
        if cat:
            lines.append(f"CATEGORIES:{escape_text(cat)}")

        # Status
        lines.append("STATUS:CONFIRMED")
        lines.append("TRANSP:OPAQUE")

        # Alarms / Reminders
        # Event specific reminders or global defaults
        reminders = ev.get("reminders")
        if reminders is None:
            reminders = global_reminders

        for rem in reminders:
            if isinstance(rem, int):
                # Trigger in minutes relative to start, e.g. -1440 for 24h before
                lines.extend(build_valarm(rem, description=f"Reminder: {title}"))
            elif isinstance(rem, dict):
                trig = rem.get("trigger_minutes", -1440)
                desc_alarm = rem.get("description", f"Reminder: {title}")
                lines.extend(build_valarm(trig, description=desc_alarm))

        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    # Apply RFC 5545 line folding and join with CRLF
    folded_lines = [rfc5545_fold_line(l) for l in lines]
    return "\r\n".join(folded_lines) + "\r\n"

def main():
    parser = argparse.ArgumentParser(description="Generate RFC 5545 iCalendar (.ics) files from JSON")
    parser.add_argument("-i", "--input", help="Path to input JSON file. If omitted, reads from stdin.")
    parser.add_argument("-o", "--output", help="Path to output .ics file. If omitted, prints to stdout.")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    ics_content = generate_ics(data)

    if args.output:
        # Ensure parent directory exists
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, "wb") as f:
            f.write(ics_content.encode("utf-8"))
        print(f"Successfully wrote {len(data.get('events', []))} events to {os.path.abspath(args.output)}")
    else:
        sys.stdout.write(ics_content)

if __name__ == "__main__":
    main()
