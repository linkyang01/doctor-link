#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-DoctorLinkValidation}"
rm -rf "$ROOT_DIR"
mkdir -p "$ROOT_DIR"
cd "$ROOT_DIR"

mkdir -p VlyTestLibrary/01-BasicFormats logs
printf 'sample video placeholder\n' > VlyTestLibrary/01-BasicFormats/sample.mp4
printf 'subtitle placeholder\n' > VlyTestLibrary/01-BasicFormats/sample.srt
printf 'audio placeholder\n' > VlyTestLibrary/01-BasicFormats/sample.dts
printf 'password=validation-secret user@example.com\n' > logs/app.log
printf 'attachment placeholder\n' > VlyTestLibrary/input.txt

doctor-link --help >/dev/null
doctor-link init DoctorWorkspace >/dev/null
doctor-link scan VlyTestLibrary >/dev/null
doctor-link plan VlyTestLibrary >/dev/null
doctor-link report VlyTestLibrary --out DoctorReports >/dev/null

PACKAGE_DIR=$(find DoctorReports -mindepth 1 -maxdepth 1 -type d | head -n 1)
test -n "$PACKAGE_DIR"
test -f "$PACKAGE_DIR/doctor-report.json"
test -f "$PACKAGE_DIR/summary.md"

doctor-link schema validate "$PACKAGE_DIR" --write --json >/dev/null
test -f "$PACKAGE_DIR/schema-validation-result.json"

mkdir -p ConformanceFixtures/valid ConformanceFixtures/invalid ConformanceFixtures/backward-compatible ConformanceFixtures/migration
cp -R "$PACKAGE_DIR" ConformanceFixtures/valid/generated-valid
cp -R "$PACKAGE_DIR" ConformanceFixtures/backward-compatible/generated-legacy
cp -R "$PACKAGE_DIR" ConformanceFixtures/migration/generated-migration
cp -R "$PACKAGE_DIR" ConformanceFixtures/invalid/generated-invalid
rm -f ConformanceFixtures/invalid/generated-invalid/doctor-report.json

doctor-link conformance run ConformanceFixtures --out DoctorReports/conformance --json >/dev/null
test -f DoctorReports/conformance/conformance-report.json

cp "$PACKAGE_DIR/doctor-report.json" DoctorReports/before-validation.json

doctor-link collect "$PACKAGE_DIR" \
  --project-root . \
  --logs "logs/*.log" \
  --command "python --version" \
  --attachment VlyTestLibrary/input.txt \
  --note "P5.9 validation evidence" \
  --redact-email \
  --redact-pattern "validation-secret" >/dev/null

test -f "$PACKAGE_DIR/redaction-report.md"

doctor-link assert "$PACKAGE_DIR" \
  --statement "Validation user-confirmed issue" \
  --expected "Expected behavior" \
  --actual "Actual behavior" >/dev/null

test -f "$PACKAGE_DIR/user-assertions.json"

doctor-link record "$PACKAGE_DIR" \
  --name "Validation smoke" \
  --status partial \
  --expected "Validation should produce package outputs" \
  --actual "Validation generated placeholder outputs" >/dev/null

doctor-link compare DoctorReports/before-validation.json "$PACKAGE_DIR/doctor-report.json" \
  --out DoctorReports/comparison-validation \
  --package-dir "$PACKAGE_DIR" >/dev/null

if doctor-link verify "$PACKAGE_DIR" --write-back --json > DoctorReports/verification-validation.json; then
  echo "Expected the partial validation record to keep verification blocked" >&2
  exit 1
fi
grep -q '"status": "not_verified"' DoctorReports/verification-validation.json
test -f "$PACKAGE_DIR/verification-result.json"

doctor-link schema validate "$PACKAGE_DIR" --write --json >/dev/null

doctor-link handoff "$PACKAGE_DIR" --tool codex --out DoctorReports/handoff-validation >/dev/null
test -f DoctorReports/handoff-validation/handoff-manifest.json

doctor-link view "$PACKAGE_DIR" --build-only >/dev/null
test -f "$PACKAGE_DIR/.doctorlink-web/index.html"

BEFORE_PACKAGE=$(doctor-link diagnose before --project "Validation" --summary "before validation" --out DoctorReports | awk -F': ' '/Created before package/ {print $2}')
test -n "$BEFORE_PACKAGE"
test -f "$BEFORE_PACKAGE/doctor-report.json"

doctor-link schema validate "$BEFORE_PACKAGE" --write --json >/dev/null

AFTER_PACKAGE=$(doctor-link diagnose after --project "Validation" --summary "after validation" --before-package "$BEFORE_PACKAGE" --out DoctorReports | awk -F': ' '/Created after package/ {print $2}')
test -n "$AFTER_PACKAGE"
test -f "$AFTER_PACKAGE/doctor-report.json"

doctor-link diagnose compare "$AFTER_PACKAGE" --json >/dev/null
if doctor-link diagnose verify "$AFTER_PACKAGE" --json > DoctorReports/diagnosis-verification-validation.json; then
  echo "Expected the evidence-free after package to remain incomplete" >&2
  exit 1
fi
grep -q '"success": false' DoctorReports/diagnosis-verification-validation.json
doctor-link schema validate "$AFTER_PACKAGE" --write --json >/dev/null

doctor-link health DoctorReports --json >/dev/null
test -f DoctorReports/project-health.json

echo "Doctor link validation completed successfully."
