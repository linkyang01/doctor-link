# CLI Command Reference

Doctor link CLI command:

```bash
doctor-link <command>
```

## Workspace and reports

```bash
doctor-link init [workspace]
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link legacy-report <library> --out DoctorReports
```

## Evidence collection

```bash
doctor-link env --project-root . --out environment.json
doctor-link probe <file> --summary --out probe.json
doctor-link collect <package_dir> --project-root . --logs "logs/*.log" --command "python --version"
doctor-link record <package_dir> --name "Test name" --status partial --assertion-id assertion-1
doctor-link vly-proof <library> --package-dir <package_dir>
```

## Assertions and verification

```bash
doctor-link assert <package_dir> --statement "This is the problem"
doctor-link verify <package_dir> --write-back
doctor-link compare before.json after.json --package-dir <package_dir>
doctor-link doctor-package <package_dir> --out DoctorReports/package.zip
```

## Local workbench

```bash
doctor-link view <package_dir>
doctor-link view <package_dir> --build-only
doctor-link view DoctorReports --build-only
```

## AI Coding collaboration

```bash
doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ai-result <package_dir> --summary "AI repair summary" --claimed-fix "claimed fix"
doctor-link diagnosis-history <package_dir> --ai-pass "round 1" --user-correction "human correction"
doctor-link assertion-check <package_dir>
doctor-link risk-review <package_dir> --file doctor_link/cli.py --boundary doctor_link/
```

## Automated diagnosis pipeline

```bash
doctor-link strategy validate . --json
doctor-link reproduce list . --json
doctor-link reproduce run <reproduction_id> . --package-dir <package_dir> --json
doctor-link test list . --json
doctor-link test run . --job <job_id> --package-dir <package_dir> --json
doctor-link diagnose before --project "Demo" --summary "before issue" --out DoctorReports
doctor-link diagnose after --project "Demo" --summary "after fix" --before-package <before_package> --out DoctorReports
doctor-link diagnose compare <after_package> --json
doctor-link diagnose verify <after_package> --json
doctor-link health DoctorReports --json
```

## Exit behavior

Most commands print output paths and return non-zero when validation fails or inputs are invalid.

## Safety boundary

CLI commands are local-first. They do not publish releases or upload diagnostic packages by default.
