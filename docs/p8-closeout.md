# P8 closeout

P8 is complete.

## Completed

- `doctor-link diagnose-now` creates `summary.md`.
- The default output is `.doctor-link/summary.md`.
- `--output` writes the summary to a custom directory.
- `--json` prints the summary path for automation.
- Output directories are excluded from scans.

## Covered by tests

- repeated runs do not count generated output
- extension counts are reported
- custom output directory works
- `--json` with `--output` writes and