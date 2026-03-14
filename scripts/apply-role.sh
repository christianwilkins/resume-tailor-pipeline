#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: scripts/apply-role.sh <company-slug> <job-url>" >&2
  exit 1
fi

company="$1"
url="$2"
company_dir="applications/${company}"
version_dir="versions/${company}"

mkdir -p "$company_dir" "$version_dir"

skills/resume-tailor/scripts/fetch_job_posting.py "$url" job-posting.txt >/dev/null
cp job-posting.txt "${company_dir}/job-posting.txt"

cat <<MSG
Prepared role workspace for '${company}'.

Updated:
- job-posting.txt
- ${company_dir}/job-posting.txt

Next steps:
1. Tailor resume.tex from master-resume.tex.
2. Validate with skills/resume-tailor/scripts/check_one_page.sh resume.tex.
3. Save final artifacts into ${version_dir}/.
MSG
