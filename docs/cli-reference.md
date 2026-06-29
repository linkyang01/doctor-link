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
doctor-link workbench-note <package_dir> --note "Reviewed" --enable-write-back --json
```

## No-code guided workflow

```bash
doctor-link wizard --folder . --summary "startup issue" --tool cursor --handoff --json
doctor-link diagnose-now . --full --handoff --tool grok --json
doctor-link home --reports DoctorReports
```

## AI Coding collaboration

```bash
doctor-link handoff list
doctor-link handoff list --json
doctor-link handoff check <package_dir> --tool grok --json
doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link handoff <package_dir> --tool codex --json
doctor-link handoff generate <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ai-result <package_dir> --summary "AI repair summary" --claimed-fix "claimed fix"
doctor-link diagnosis-history <package_dir> --ai-pass "round 1" --user-correction "human correction"
doctor-link assertion-check <package_dir>
doctor-link risk-review <package_dir> --file doctor_link/cli.py --boundary doctor_link/
```

Supported `--tool` profiles: `aider`, `claude-code`, `cline`, `codex`, `continue`, `cursor`, `generic`, `grok`, `openhands`, `windsurf`. Default for guided handoff generation: `cursor`.

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

## CI and distribution readiness

```bash
doctor-link ci report DoctorReports --out DoctorReports/ci --json
doctor-link distribution check . --dist dist --out DoctorReports/distribution --json
```

## Adapter runtime

```bash
doctor-link adapter list . --json
doctor-link adapter validate .doctorlink/adapters/demo-adapter/adapter.yml --json
doctor-link adapter run demo-adapter verification . --out DoctorReports/adapters --json
```

`adapter run` is a dry-run by default. It validates the manifest and writes an audit/run record without executing the configured local command. To execute the adapter command, pass explicit approval:

```bash
doctor-link adapter run demo-adapter verification . --allow-run --out DoctorReports/adapters --json
```

## Plugin runtime

```bash
doctor-link plugin list . --json
doctor-link plugin validate .doctorlink/plugins/demo-plugin/plugin.yml --json
doctor-link plugin run demo-plugin verification . --out DoctorReports/plugins --json
```

`plugin run` is a dry-run by default. It validates the manifest and writes an audit/run record without executing the configured local command. To execute the plugin command, pass explicit approval:

```bash
doctor-link plugin run demo-plugin verification . --allow-run --out DoctorReports/plugins --json
```

## Integrity and privacy gates

```bash
doctor-link integrity manifest . --out DoctorReports/integrity-manifest.json --json
doctor-link integrity verify . DoctorReports/integrity-manifest.json --json
doctor-link integrity verify . DoctorReports/integrity-manifest.json --strict --json
doctor-link privacy scan . --out DoctorReports/privacy-scan.json --json
doctor-link privacy redaction-gate . --out DoctorReports/redaction-gate.json --json
doctor-link privacy export-gate . --manifest DoctorReports/integrity-manifest.json --out DoctorReports/export-gate.json --json
```

## Knowledge and archive runtime

```bash
doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json --json
doctor-link knowledge query DoctorReports/knowledge-index.json "missing evidence" --json
doctor-link knowledge export DoctorReports/knowledge-index.json DoctorReports/knowledge-export.json --json
doctor-link archive create DoctorReports-source DoctorReports/archive --metadata owner=qa --json
doctor-link archive inspect DoctorReports/archive --json
doctor-link archive policy-check DoctorReports/archive --max-files 1000 --json
doctor-link archive export DoctorReports/archive DoctorReports/archive.zip --json
```

`archive create` requires the archive output directory to be outside the source directory. This prevents recursive self-copying and archive pollution.

## Exit behavior

Most commands print output paths and return non-zero when validation fails or inputs are invalid.

## Safety boundary

CLI commands are local-first. They do not publish releases or upload diagnostic packages by default.
