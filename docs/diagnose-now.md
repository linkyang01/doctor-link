# diagnose-now

Run a quick diagnosis for a local project folder, or run the full guided workflow in one command.

## Quick scan (default)

```bash
doctor-link diagnose-now /path/to/project
```

This writes:

```text
/path/to/project/.doctor-link/summary.md
```

The summary includes file count, extension counts, and basic recommendations.

## Custom output directory

```bash
doctor-link diagnose-now /path/to/project --output /path/to/report
```

## JSON output

```bash
doctor-link diagnose-now /path/to/project --json
```

Use `--report-json` when you also need the structured diagnosis report.

## Full guided workflow

```bash
doctor-link diagnose-now /path/to/project --full --summary "startup issue"
```

This generates a diagnostic package, collects evidence, runs verification planning, and builds the local HTML report.

## AI handoff in one command

```bash
doctor-link diagnose-now /path/to/project --handoff --tool grok --summary "startup issue"
```

`--handoff` implies `--full`. Supported `--tool` values match `doctor-link handoff list`.

Default handoff profile: `cursor`.

## Useful flags

```bash
doctor-link diagnose-now . --full --no-collect
doctor-link diagnose-now . --handoff --tool codex --reports DoctorReports --json
```

| Flag | Purpose |
|------|---------|
| `--full` | Run the complete diagnostic workflow |
| `--handoff` | Generate an AI handoff package (implies `--full`) |
| `--tool` | Handoff profile when `--handoff` is set |
| `--no-collect` | Skip automatic evidence collection |
| `--reports` | DoctorReports output directory |
| `--json` | Print workflow result as JSON |
| `--report-json` | Include structured report in JSON output |

## Related commands

```bash
doctor-link wizard --folder . --tool cursor --handoff
doctor-link handoff list
doctor-link handoff check <package_dir> --tool grok --json
doctor-link home
```