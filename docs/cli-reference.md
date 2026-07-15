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
doctor-link doctor-package <package_dir> --out DoctorReports/package.zip --json
doctor-link doctor-package <package_dir> --out DoctorReports/reviewed.zip --allow-unsafe-export
doctor-link schema migrate <package_dir> --json
```

`doctor-package` runs the privacy export gate by default and returns non-zero when sensitive patterns remain. `--allow-unsafe-export` is an explicit reviewed override and is recorded in `package-export-manifest.json`. Export manifests and package README files contain portable relative paths only.

`schema migrate` recognizes only legacy export-shaped `manifest.json` files. It writes `package-export-manifest.json`, preserves the original as `manifest.legacy-export.json`, backs up the old package README, and leaves formal package manifests untouched.

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

Configured reproduction and test commands support leading environment assignments without a shell:

```yaml
command: PYTHONPATH=src MODE=regression python -m pytest tests/test_auth.py
```

Assignments must precede the executable. Sequential `&&` commands are supported, while redirection, pipelines, command substitution, and other shell control operators remain rejected.

When `--package-dir` is supplied, each reproduction or test job writes its JSON result into the package and updates `doctor-report.json`, `evidence-list.md`, and `timeline.md`. Stable IDs replace the prior result when the same job is rerun.

## Automatic solve

For a guided path that does not require knowing a test command:

```bash
doctor-link assist /path/to/project --problem "Checkout duplicates a charge"
doctor-link explain /path/to/project \
  --problem "Checkout duplicates a charge" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --json
doctor-link solve /path/to/project \
  --problem "Checkout duplicates a charge" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --suggest-only
doctor-link diff /path/to/solve-session --json
doctor-link reproduce suggest /path/to/project --problem "Checkout duplicates a charge" --json
```

`assist` validates ranked, project-owned reproduction candidates, writes a JSON receipt and local HTML diagnostic report, prepares a normal solve preview, and attaches advisory root-cause hints when failing evidence can be clustered. Add `--allow-repair` only after reviewing the reproduction. Use `--package packages/name` for a workspace package and `--no-open` in CI or headless environments. Use `--interactive` to run, skip, or quit each candidate without rewriting the problem description.

`explain` runs the same safe checks as solve preview, then parses pytest and common JavaScript failure formats into structured failures. Its JSON and Markdown receipts include extracted expected/actual values, project-owned stack frames, exact changed lines, enclosing functions, source excerpts, candidate scores, and the evidence behind each score. If a diagnostic command changes the Git working tree, it returns `modified_worktree` (exit 5) and requires review. Hints remain advisory rather than verified root causes; Doctor link still accepts repairs only after independent re-verification. Session-based `diff` includes uncommitted edits while the recorded repair branch remains checked out.

Preview a bounded Python or Node.js JavaScript/TypeScript repair without modifying code:

```bash
doctor-link solve /path/to/project \
  --problem "Checkout creates two charges" \
  --reproduce-command "python -m pytest tests/test_checkout.py::test_single_charge -q" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --json
```

After reviewing the preview, authorize branch creation and Codex edits:

```bash
doctor-link solve /path/to/project \
  --problem "Checkout creates two charges" \
  --reproduce-command "python -m pytest tests/test_checkout.py::test_single_charge -q" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --allow-repair \
  --max-rounds 3 \
  --command-timeout 120 \
  --repair-timeout 900 \
  --json
```

The current source supports Python and Node.js JavaScript/TypeScript projects. It requires a clean Git repository and either explicit commands, configured reproduction/test catalogs, a discoverable Python `tests/` directory, a usable JavaScript package test script, or JavaScript test files compatible with `node --test`. Without `--allow-repair`, the command may reproduce the problem and write a prompt preview, but it does not create a branch, invoke Codex, or edit code. See [Automatic Solve with Codex](automatic-solve.md).

JavaScript/TypeScript test discovery respects `packageManager` and lockfiles. It selects `pnpm test`, `yarn test`, `bun run test`, or `npm test`; the default npm placeholder is ignored. In npm, Yarn, or pnpm workspaces, use `--package packages/name`; ambiguous roots are blocked and return discovered candidates. Resume an interrupted repair with `doctor-link solve --resume SESSION_DIR --allow-repair`.

By default, `solve` hash-protects tests, package manifests and lockfiles, test configuration, configured reproduction/test catalogs, and directly referenced verification scripts. If Codex changes any protected input, Doctor link returns `blocked` with `verification_inputs_modified`, even when the changed checks pass. `--allow-verification-changes` is an explicit exception that is valid only with `--allow-repair`; passing checks then return `review_required` (exit 6), never `verified`.

Run repeatable scenarios across projects with a versioned YAML or JSON manifest:

```bash
doctor-link benchmark benchmark.yml --out DoctorReports/benchmark --json
```

The benchmark reports actual failed-check reproduction, repair success, rounds, duration, blockers, and expected-status matches. Repairs are disabled unless the benchmark receives `--allow-repair`.

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

Commands print JSON before returning their final exit status, so CI can parse the result and still rely on the process code:

| Command | Exit 0 | Non-zero |
| --- | --- | --- |
| `reproduce run` | `passed` or manual reproduction | failed, timed out, missing, or invalid reproduction |
| `test run` | all required jobs passed | at least one required job failed; optional job failures remain visible but do not fail the command |
| `verify` | `candidate_verified`, `ready`, or `verified` | `missing_evidence`, `not_verified`, or another incomplete status |
| `diagnose verify` | diagnosis pipeline reports success | pipeline remains incomplete or blocked |
| `solve` | `verified` | `approval_required` (2), `not_reproduced` (3), `blocked` (4), `failed` (5), `review_required` (6), or `suggestion_ready` (7) |
| `explain` | `explained` / `partial` | `no_failures` (3) or `insufficient_evidence` (4) |
| `diff` | structured receipt | non-zero only on usage/Git errors |

See [Automated diagnosis reliability](automated-diagnosis-reliability.md) for assertion, evidence, concurrency, and handoff rules.

## Safety boundary

CLI commands are local-first. They do not publish releases or upload diagnostic packages by default. `solve` requires explicit `--allow-repair`, keeps Codex in a workspace-write sandbox, protects the original acceptance inputs, and never auto-commits or pushes the repair branch.
