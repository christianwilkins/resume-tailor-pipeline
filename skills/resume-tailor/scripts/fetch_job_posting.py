#!/usr/bin/env python3
import html
import re
import sys
import urllib.request

if len(sys.argv) < 2:
    print("usage: fetch_job_posting.py <url> [output]", file=sys.stderr)
    sys.exit(1)

url = sys.argv[1]
out_path = sys.argv[2] if len(sys.argv) > 2 else "job-posting.txt"

request = urllib.request.Request(
    url,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    },
)

with urllib.request.urlopen(request) as response:
    raw = response.read().decode("utf-8", errors="ignore")

def clean(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\\u2019", "'").replace("\\u2014", "-")
    text = text.replace("\\n", "\n").replace("\\/", "/").replace('\\"', '"')
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

title_match = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
desc_match = re.search(r'<meta name="description" content="(.*?)"', raw, re.I | re.S)

parts = []
if title_match:
    parts.append(clean(title_match.group(1)))
if desc_match:
    parts.append(clean(desc_match.group(1)))

field_titles = re.findall(r'"title":"((?:\\.|[^"])*)","isNullable":', raw)
field_titles = [clean(t) for t in field_titles]
field_titles = [t for t in field_titles if t not in {"Name", "Email", "Resume", "Submit"}]
seen = set()
unique_titles = []
for title in field_titles:
    if title and title not in seen:
        seen.add(title)
        unique_titles.append(title)

if unique_titles:
    parts.append("Application Questions")
    parts.extend(f"- {title}" for title in unique_titles)

content = "\n\n".join(parts).strip() if parts else clean(raw)
with open(out_path, "w", encoding="utf-8") as fh:
    fh.write(content + "\n")

print(out_path)
