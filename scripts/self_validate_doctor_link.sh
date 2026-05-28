#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-DoctorLinkSelfValidation}"
rm -rf "$ROOT_DIR"
mkdir -p "$ROOT_DIR" "$ROOT_DIR/logs"

printf 'Doctor link self-validation log\n' > "$ROOT_DIR/logs/self-validation.log"

doctor-link --help >/dev/null

doctor-link strategy validate . --json > "$ROOT_DIR/strategy-validation.json"
doctor-link reproduce list . --json > "$ROOT_DIR/reproductions.json"
doctor-link test list . --json > "$ROOT_DIR/test-matrix.json"

doctor-link scan doctor_link > "$ROOT_DIR/source-scan.txt"
doctor-link plan doctor_link > "$ROOT_DIR/source-plan.md"
doctor-link report doctor_link --out "$ROOT_DIR/DoctorReports" > "$ROOT_DIR/report.log"

PACKAGE_DIR=$(find "$ROOT_DIR/DoctorReports" -mindepth 1 -maxdepth 1 -type d | head -n 1)
test -n "$PACKAGE_DIR"
test -f "$PACKAGE_DIR/doctor-report.json"
test -f "$PACKAGE_DIR/summary.md"

doctor-link env --project-root . --out "$ROOT_DIR/environment.json"

doctor-link collect "$PACKAGE_DIR" \
  --project-root . \
  --logs "$ROOT_DIR/logs/*.log" \
  --command "python --version" \
  --command "doctor-link --help" \
  --attachment pyproject.toml \
  --note "Doctor link self-validation evidence" \
  --redact-email >/dev/null

doctor-link assert "$PACKAGE_DIR" \
  --statement "Doctor link CLI self-validation should run successfully" \
  --expected "Self-validation commands complete and generate diagnostic outputs" \
  --actual "Self-validation generated diagnostic package and evidence" >/dev/null

doctor-link record "$PACKAGE_DIR" \
  --name "Doctor link self-validation" \
  --status passed \
  --expected "Doctor link can diagnose its own repository" \
  --actual "Doctor link generated a self-diagnostic package" >/dev/null

doctor-link verify "$PACKAGE_DIR" --write-back >/dev/null
test -f "$PACKAGE_DIR/verification-result.json"

doctor-link handoff "$PACKAGE_DIR" --tool generic --out "$ROOT_DIR/handoff" >/dev/null
test -f "$ROOT_DIR/handoff/handoff-manifest.json"

doctor-link view "$PACKAGE_DIR" --build-only >/dev/null
test -f "$PACKAGE_DIR/.doctorlink-web/index.html"

doctor-link health "$ROOT_DIR/DoctorReports" --json > "$ROOT_DIR/project-health.json"
test -f "$ROOT_DIR/DoctorReports/project-health.json"

cat > "$ROOT_DIR/self-validation-summary.md" <<'SUMMARY'
# Doctor link Self-validation Summary

Result: success

Doctor link successfully diagnosed its own repository by scanning the source package, generating a diagnostic package, collecting evidence, recording a user assertion, recording a validation result, writing verification output, creating an AI handoff package, building a local web view, and generating a project health summary.
SUMMARY

echo "Doctor link self-validation completed successfully."
