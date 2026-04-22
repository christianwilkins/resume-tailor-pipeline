#!/usr/bin/env python3
from __future__ import annotations

import argparse
import statistics
import subprocess
import sys
import tempfile
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


@dataclass
class Line:
    text: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def words(self) -> int:
        return len([w for w in self.text.split() if w])


@dataclass
class Block:
    lines: list[Line]

    @property
    def last_line(self) -> Line:
        return self.lines[-1]

    @property
    def previous_lines(self) -> list[Line]:
        return self.lines[:-1]

    @property
    def preview(self) -> str:
        return " ".join(line.text for line in self.lines)[:140]


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True)


def get_page_count(pdf_path: Path) -> int:
    output = run(["pdfinfo", str(pdf_path)])
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"Could not determine page count for {pdf_path}")


def parse_bbox_lines(pdf_path: Path) -> tuple[float, float, list[Line]]:
    raw = run(["pdftotext", "-bbox-layout", str(pdf_path), "-"])
    root = ET.fromstring(raw)

    page = next(elem for elem in root.iter() if elem.tag.endswith("page"))
    page_width = float(page.attrib["width"])
    page_height = float(page.attrib["height"])

    all_lines: list[Line] = []

    for line_el in page.iter():
        if not line_el.tag.endswith("line"):
            continue
        words = [w.text or "" for w in line_el if w.tag.endswith("word")]
        text = " ".join(w.strip() for w in words if w.strip())
        if not text.strip():
            continue
        all_lines.append(
            Line(
                text=text,
                x_min=float(line_el.attrib["xMin"]),
                x_max=float(line_el.attrib["xMax"]),
                y_min=float(line_el.attrib["yMin"]),
                y_max=float(line_el.attrib["yMax"]),
            )
        )

    return page_width, page_height, all_lines


def extract_bullet_groups(lines: list[Line]) -> list[Block]:
    ordered = sorted(lines, key=lambda line: (line.y_min, line.x_min))
    bullets: list[Block] = []
    i = 0

    while i < len(ordered):
        line = ordered[i]

        is_bullet_start = 40.0 <= line.x_min <= 45.5 and line.text.lstrip().startswith("•")
        if not is_bullet_start:
            i += 1
            continue

        group = [line]
        j = i + 1
        while j < len(ordered):
            nxt = ordered[j]
            vertical_gap = nxt.y_min - group[-1].y_min
            if vertical_gap > 18.5:
                break

            is_continuation = nxt.x_min >= group[0].x_min + 8.0
            if not is_continuation:
                break

            group.append(nxt)
            j += 1

        bullets.append(Block(lines=group))
        i = j

    return bullets


def measure_bottom_whitespace_image(pdf_path: Path) -> float | None:
    if Image is None:
        return None

    with tempfile.TemporaryDirectory() as td:
        out_base = Path(td) / "page"
        subprocess.check_call(
            [
                "pdftoppm",
                "-gray",
                "-png",
                "-singlefile",
                "-f",
                "1",
                "-l",
                "1",
                str(pdf_path),
                str(out_base),
            ]
        )
        image_path = out_base.with_suffix(".png")
        img = Image.open(image_path).convert("L")
        width, height = img.size
        threshold = 245
        cutoff = None
        for y in range(height - 1, -1, -1):
            row = [img.getpixel((x, y)) for x in range(width)]
            dark_ratio = sum(1 for px in row if px < threshold) / max(1, width)
            if dark_ratio > 0.003:
                cutoff = y
                break
        if cutoff is None:
            return 100.0
        blank_px = height - 1 - cutoff
        return (blank_px / height) * 100.0


def estimate_bottom_whitespace_text(page_height: float, lines: Iterable[Line]) -> float:
    max_y = max((line.y_max for line in lines), default=0.0)
    return ((page_height - max_y) / page_height) * 100.0


def find_widows(blocks: list[Block], page_width: float) -> list[dict]:
    findings: list[dict] = []
    for block in blocks:
        if len(block.lines) < 2:
            continue

        if block.lines[0].y_min < 70:
            continue

        prev_widths = [line.width for line in block.previous_lines if line.words >= 3]
        if not prev_widths:
            continue

        baseline = statistics.median(prev_widths)
        last = block.last_line
        ratio = last.width / baseline if baseline else 1.0
        page_ratio = last.width / page_width if page_width else 1.0

        looks_short = ratio < 0.50 or page_ratio < 0.50
        very_few_words = last.words <= 4

        if looks_short or very_few_words:
            findings.append(
                {
                    "text": last.text,
                    "preview": block.preview,
                    "ratio": round(ratio, 3),
                    "page_ratio": round(page_ratio, 3),
                    "words": last.words,
                    "y_min": round(last.y_min, 1),
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check resume layout fullness and widow lines")
    parser.add_argument("pdf", nargs="?", default="resume.pdf")
    parser.add_argument("--max-bottom-whitespace-pct", type=float, default=10.0)
    parser.add_argument("--max-widows", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Missing PDF: {pdf_path}", file=sys.stderr)
        return 2

    page_count = get_page_count(pdf_path)
    page_width, page_height, all_lines = parse_bbox_lines(pdf_path)
    blocks = extract_bullet_groups(all_lines)
    whitespace_text = estimate_bottom_whitespace_text(page_height, all_lines)
    whitespace_image = measure_bottom_whitespace_image(pdf_path)
    widows = find_widows(blocks, page_width)

    effective_whitespace = whitespace_image if whitespace_image is not None else whitespace_text

    failures: list[str] = []
    if page_count != 1:
        failures.append(f"expected 1 page, found {page_count}")
    if effective_whitespace > args.max_bottom_whitespace_pct:
        failures.append(
            f"bottom whitespace {effective_whitespace:.2f}% exceeds {args.max_bottom_whitespace_pct:.2f}%"
        )
    if len(widows) > args.max_widows:
        failures.append(f"found {len(widows)} widow candidates, max allowed is {args.max_widows}")

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "pdf": str(pdf_path),
                    "page_count": page_count,
                    "bottom_whitespace_text_pct": round(whitespace_text, 2),
                    "bottom_whitespace_image_pct": None if whitespace_image is None else round(whitespace_image, 2),
                    "widow_count": len(widows),
                    "widows": widows,
                    "pass": not failures,
                    "failures": failures,
                },
                indent=2,
            )
        )
    else:
        print(f"PDF: {pdf_path}")
        print(f"Pages: {page_count}")
        print(f"Bottom whitespace (text): {whitespace_text:.2f}%")
        if whitespace_image is not None:
            print(f"Bottom whitespace (image): {whitespace_image:.2f}%")
        else:
            print("Bottom whitespace (image): unavailable, Pillow missing")
        print(f"Widow candidates: {len(widows)}")
        for item in widows[:10]:
            print(textwrap.shorten(f"- {item['text']} | preview: {item['preview']}", width=180, placeholder="..."))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print("PASS: resume layout checks look good")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
