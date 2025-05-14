
import re
import dateparser

pattern = re.compile(r'(.+?)\s*-\s*(.+?)(\s*\([^)]+\))?$', re.IGNORECASE)

def parse_experience(text):
    parts = re.split(r'\n\s*\n', text)
    results = []
    i = 0
    while i < len(parts) - 1:
        head = parts[i].splitlines()
        body = parts[i+1].splitlines()
        if not body:
            i += 2
            continue
        match = pattern.search(body[0])
        if not match:
            i += 2
            continue
        start, end, duration = match.groups()
        start_date = dateparser.parse(start, languages=['es','en'])
        end_date = dateparser.parse(end, languages=['es','en']) if 'present' not in end.lower() else None
        entry = {
            "company": head[0].strip() if head else "Unknown",
            "title": head[1].strip() if len(head) > 1 else "Not specified",
            "startDate": start_date.strftime("%Y-%m") if start_date else start,
            "endDate": end_date.strftime("%Y-%m") if end_date else "Present"
        }
        if duration:
            entry["duration"] = duration.strip()
        results.append(entry)
        i += 2
    return results

def process(data):
    if "Experience" in data and isinstance(data["Experience"], str):
        data["Experience"] = parse_experience(data["Experience"])
    return data
