# Workflow

## Source of Truth

- `master-resume.tex` is canonical.
- `resume.tex` is the current tailored output.
- `job-posting.txt` is the local cached role description for the current run.

## Output Locations

- Tailored resume source: `resume.tex`
- Generated PDF: `resume.pdf`
- Company answers: `applications/<company>/answers.md`
- Reusable prompt: `prompts/tailor-resume.md`

## Selection Heuristics

1. Start with the top 2-3 experiences that best match the role's stack and operating style.
2. Keep 2-3 projects that reinforce missing keywords or product-building signal.
3. Cut leadership/community items first when space is tight unless the role strongly emphasizes people leadership.
4. Prefer one strong bullet over two generic bullets.
5. Use measured outcomes whenever the master resume includes them.

## Validation

Run `skills/resume-tailor/scripts/check_one_page.sh resume.tex` after edits.
Then run `python3 scripts/check_resume_layout.py resume.pdf`.
The first check enforces one page. The second checks first-page fullness plus bullet widow quality using first-page line geometry.
