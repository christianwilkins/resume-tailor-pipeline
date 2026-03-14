---
name: resume-tailor
description: Tailor this repo's one-page LaTeX resume and short application answers from master-resume.tex plus a target job posting or URL. Use when adapting the resume to a specific role, fetching a live posting, validating one-page output, or saving company-specific application answers.
---

# Resume Tailor

Use this skill for this repo's standard application workflow.

## Inputs

- `master-resume.tex`: source of truth; never edit it.
- `job-posting.txt`: plain-text role description when already available.
- A live job URL: fetch it first if `job-posting.txt` is stale or missing.

## Workflow

1. If the user gives a URL, prefer `scripts/apply-role.sh <company-slug> <url>`. If only a raw fetch is needed, run `skills/resume-tailor/scripts/fetch_job_posting.py <url> job-posting.txt`.
2. Read `master-resume.tex` and extract the best subset for the role.
3. Read `job-posting.txt` and identify must-haves, role keywords, company values, and any application questions.
4. Write `resume.tex` only from facts present in `master-resume.tex`.
5. Align wording to the role truthfully, but do not invent technologies, outcomes, titles, dates, or metrics.
6. Draft company-specific answers into `applications/<company>/answers.md`.
7. Validate the PDF with `skills/resume-tailor/scripts/check_one_page.sh resume.tex`.

## Resume Rules

- Keep `resume.tex` to exactly one page unless the user asks otherwise.
- Prefer the highest-signal subset over trying to squeeze everything in.
- Every kept line should prove one of: technical depth, ownership, product velocity, customer impact, or direct role match.
- Keep the skills section consistent with technologies named elsewhere in the resume.
- Preserve the existing LaTeX macros and formatting patterns unless a layout change is necessary to stay on one page.

## Application Answers

- Keep answers concise and specific.
- Match the company tone without sounding rehearsed.
- Avoid generic enthusiasm; anchor claims in one or two concrete examples from the resume.
- If an answer requires personal facts not present in the repo, write a clear placeholder instead of guessing.

## References

- Read `references/workflow.md` for repo conventions and output locations.
