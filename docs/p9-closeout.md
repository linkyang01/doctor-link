# P9 closeout

P9 completed the structured diagnosis report work.

## Completed scope

- Added `doctor_link.diagnose_report.build_report(files)`.
- Kept `diagnose-now` Markdown summary output compatible.
- Reused the report model when rendering `summary.md`.
- Added `--report-json` for structured report output.
- Preserved existing `--json` behavior.
- Added regression coverage for report JSON output.
- Documented `--report-json` in `docs/diagnose-now.md` and README.

## Merged PRs

- #129 P9 verify report test
- #130 P9 use report model for diagnose summary
- #131 P9 add report JSON output
- #132 P9 document report JSON output

## Compatibility guarantees

- Default `diagnose-now` output is unchanged.
- Existing `--json` output remains `{"summary": "..."}`.
- `summary.md` continues to be written for normal, JSON, and report JSON runs.

P9 is complete.
