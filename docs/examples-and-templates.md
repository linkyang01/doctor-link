# Examples and Templates

Doctor link examples are designed to be copied into real projects and adapted gradually.

## Example project

### Basic project

`examples/basic-project/` contains:

- a minimal Python script;
- `.doctorlink/diagnosis.yml`;
- `.doctorlink/reproduce.yml`;
- `.doctorlink/test-matrix.yml`.

Useful commands:

```bash
doctor-link strategy validate examples/basic-project --json
doctor-link reproduce list examples/basic-project --json
doctor-link test run examples/basic-project --json
```

### Multi-bug shop service

`examples/shop-service-multi-bug/` contains a richer local-only case with six known issues across auth, API, database, and cache subsystems.

One-click run:

```bash
bash examples/shop-service-multi-bug/run-example.sh
```

Useful commands:

```bash
doctor-link strategy validate examples/shop-service-multi-bug --json
doctor-link reproduce list examples/shop-service-multi-bug --json
doctor-link reproduce run repro-login-timeout examples/shop-service-multi-bug --json
doctor-link test run examples/shop-service-multi-bug --json
doctor-link report examples/shop-service-multi-bug --out DoctorReports
```

## Example diagnostic package flow

```bash
doctor-link report examples/basic-project --out DoctorReports
PACKAGE_DIR=$(find DoctorReports -mindepth 1 -maxdepth 1 -type d | head -n 1)
doctor-link collect "$PACKAGE_DIR" --project-root examples/basic-project --command "python sample_app.py"
doctor-link verify "$PACKAGE_DIR" --write-back
```

## Example AI handoff package

```bash
doctor-link handoff "$PACKAGE_DIR" --tool codex --out DoctorReports/example-handoff
```

Generated handoff packages should include:

- `handoff-manifest.json`;
- tool-specific instruction file;
- diagnostic context files copied from the package.

## Example before / after workflow

```bash
doctor-link diagnose before --project "Example" --summary "before issue" --out DoctorReports
doctor-link diagnose after --project "Example" --summary "after fix" --before-package <before_package> --out DoctorReports
doctor-link diagnose verify <after_package> --json
```

## Example verification result

`verification-result.json` records whether evidence is complete. Pipeline success remains false when verification evidence is missing.

## Template gallery

Recommended templates:

- `.doctorlink/diagnosis.yml` for project strategy;
- `.doctorlink/reproduce.yml` for reproduction steps;
- `.doctorlink/test-matrix.yml` for executable test jobs;
- `ai-task.md` for AI repair handoff;
- `fix-verification-checklist.md` for verification closure.
