#!/usr/bin/env bash
set -euo pipefail

tex_file="${1:-resume.tex}"
base="${tex_file%.tex}"

latexmk -pdf -interaction=nonstopmode "$tex_file" >/tmp/check_one_page.log

line=$(rg 'Output written on .*\(([0-9]+) page' "${base}.log" | tail -n 1 || true)
if [[ -z "$line" ]]; then
  echo "Could not determine page count from ${base}.log" >&2
  exit 1
fi

pages=$(printf '%s' "$line" | sed -E 's/.*\(([0-9]+) page.*/\1/')
if [[ "$pages" != "1" ]]; then
  echo "Expected 1 page, got ${pages}" >&2
  exit 1
fi

echo "OK: ${tex_file} compiles to 1 page"
