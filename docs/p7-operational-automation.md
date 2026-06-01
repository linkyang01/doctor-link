# P7.4 Operational Automation Hardening

Status: runtime implementation

## Scope

P7.4 turns P4 operational automation into CI-friendly runtime reporting.

It adds a local-first CI reporting layer that can be used in GitHub Actions or other CI runners without requiring hosted services, external accounts, telemetry, or cloud uploads.

## Implemented runtime changes

### CI report generation

New command:

```bash
doctor-link ci report <reports_dir> --out <output_dir>
```

The command writes:

```text
ci-report.json
ci-report.md
github-step-summary.md
ci-artifact-index.json
project-health-trend.json
```

### GitHub Actions Markdown report

`github-step-summary.md` is a concise CI summary suitable for appending to `$GITHUB_STEP_SUMMARY` in GitHub Actions.

It includes:

- CI status;
- diagnostic package count;
- regression score;
- failed test job count;
- top failure triage;
- report artifacts.

### Failure triage summary

The CI automation report inspects diagnostic packages for:

- missing or failed verification;
- missing evidence;
- unsuccessful diagnosis pipeline summaries;
- comparison regressions or unresolved signals.

Failures are classified as:

- `blocking`;
- `warning`.

### Before / after regression score

The CI automation report computes a local regression score from:

- blocking triage items;
- warning triage items;
- failed test matrix jobs;
- declining health trend.

The score is bounded from `0` to `100`.

### Test matrix aggregation

The CI automation report aggregates JSON files under:

```text
evidence/test-results/*.json
```

It reports:

- total jobs;
- passed jobs;
- failed jobs;
- job ids;
- return codes;
- package names;
- evidence paths.

### Project health trend

The CI automation report derives a health trend from DoctorReports packages and records:

- source package count;
- point-level package scores;
- average score;
- direction: `stable`, `improving`, or `declining`.

### CI artifact index

The CI automation report indexes generated artifacts and existing report files with:

- path;
- relative path;
- root;
- kind;
- size bytes.

## CLI examples

Generate local CI artifacts:

```bash
doctor-link ci report DoctorReports --out DoctorReports/ci
```

Print JSON:

```bash
doctor-link ci report DoctorReports --json
```

Use in GitHub Actions:

```bash
doctor-link ci report DoctorReports --out DoctorReports/ci
cat DoctorReports/ci/github-step-summary.md >> "$GITHUB_STEP_SUMMARY"
```

## Safety boundaries

P7.4 does not:

- post comments to GitHub;
- require GitHub tokens;
- upload artifacts;
- call external APIs;
- introduce telemetry;
- publish releases;
- create tags;
- publish to PyPI.

The generated artifacts are local files that CI workflows may upload if separately configured.

## Validation

P7.4 includes tests for:

- CI report generation;
- GitHub step summary generation;
- failure triage;
- regression score;
- test matrix aggregation;
- project health trend;
- artifact index;
- CLI markdown output;
- CLI JSON output.
