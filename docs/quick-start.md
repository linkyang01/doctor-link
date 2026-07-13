# Quick Start

This guide gets Doctor link running locally from source.

## 1. Install

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
python -m pip install --upgrade pip
python -m pip install -e .
```

Verify:

```bash
doctor-link --help
doctor-link --version
doctor-link preflight . --json
```

`preflight` is read-only. It inspects configuration, configured commands, runtime catalogs, Python version, and local tools without executing repository commands. Resolve blockers before collecting or running project evidence.

## 2. Create a diagnostic package

```bash
mkdir -p VlyTestLibrary/01-BasicFormats
echo sample > VlyTestLibrary/01-BasicFormats/sample.mp4

doctor-link report VlyTestLibrary --out DoctorReports
```

Find the package:

```bash
PACKAGE_DIR=$(find DoctorReports -mindepth 1 -maxdepth 1 -type d | head -n 1)
```

## 3. Add evidence

```bash
doctor-link collect "$PACKAGE_DIR" --project-root . --command "python --version" --note "quick start evidence"
```

## 4. Add a human-confirmed issue

```bash
doctor-link assert "$PACKAGE_DIR" --statement "This is the problem" --expected "Expected behavior" --actual "Actual behavior"
```

## 5. Verify

```bash
doctor-link verify "$PACKAGE_DIR" --write-back
```

Doctor link does not mark a fix complete just because AI says it is fixed. Verification evidence is required.

## 6. Open local workbench

```bash
doctor-link view "$PACKAGE_DIR" --build-only
```

Open:

```text
$PACKAGE_DIR/.doctorlink-web/index.html
```

## 7. AI Coding handoff

```bash
doctor-link handoff "$PACKAGE_DIR" --tool codex --out DoctorReports/handoff
```

Use the generated instruction file with your AI Coding tool.

## 8. P4 pipeline commands

```bash
doctor-link strategy validate . --json
doctor-link reproduce list . --json
doctor-link test list . --json
doctor-link diagnose before --project "Demo" --summary "before" --out DoctorReports
doctor-link health DoctorReports --json
```

For a complete runnable scenario with known passing and failing checks:

```bash
bash examples/shop-service-multi-bug/run-example.sh
```

The script succeeds only when Doctor link correctly captures the known failures, returns non-zero from the failing subcommands, records assertion-linked evidence, keeps verification at `not_verified`, and emits a `needs_repair` handoff. See [Automated diagnosis reliability](automated-diagnosis-reliability.md).

## 9. Automatically solve a Python problem

Start with a preview. This executes the check but does not edit code:

```bash
doctor-link solve /path/to/python-project \
  --problem "The total is rounded before tax" \
  --test-command "python -m pytest tests/test_totals.py -q"
```

When the result is `approval_required`, review the generated prompt and authorize the repair:

```bash
doctor-link solve /path/to/python-project \
  --problem "The total is rounded before tax" \
  --test-command "python -m pytest tests/test_totals.py -q" \
  --allow-repair
```

The target must be a clean Git repository. Doctor link creates a `doctor-link/solve-*` branch, invokes Codex with workspace-write sandboxing, and independently reruns the check after every repair round. See [Automatic Solve with Codex](automatic-solve.md).

## Boundary

Quick start commands are local. They do not publish releases, upload packages, or require paid cloud services. Diagnostic packages can contain sensitive project evidence; inspect redaction and privacy results before sharing them or attaching them to a GitHub issue.
