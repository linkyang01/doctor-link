#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-$(pwd)}"
WORK_DIR="${ROOT_DIR}/.doctorlink-e2e"
REPORTS_DIR="${WORK_DIR}/DoctorReports"
LIB_DIR="${WORK_DIR}/VlyTestLibrary"

rm -rf "${WORK_DIR}"
mkdir -p "${LIB_DIR}/01-BasicFormats" "${WORK_DIR}/logs"

echo "sample" > "${LIB_DIR}/01-BasicFormats/sample.mp4"
echo "subtitle" > "${LIB_DIR}/01-BasicFormats/sample.srt"
echo "password=e2e-secret user@example.com" > "${LIB_DIR}/app.log"
echo "attachment" > "${LIB_DIR}/input.txt"

doctor-link --help >/dev/null
doctor-link report "${LIB_DIR}" --out "${REPORTS_DIR}"
PACKAGE_DIR=$(find "${REPORTS_DIR}" -mindepth 1 -maxdepth 1 -type d | head -n 1)
doctor-link schema validate "${PACKAGE_DIR}" --write --json >/dev/null

doctor-link collect "${PACKAGE_DIR}" --project-root "${ROOT_DIR}" --logs "${LIB_DIR}/*.log" --command "python --version" --attachment "${LIB_DIR}/input.txt" --note "E2E validation" --redact-email
doctor-link assert "${PACKAGE_DIR}" --statement "E2E user-confirmed issue" --expected "Expected behavior" --actual "Actual behavior"
doctor-link verify "${PACKAGE_DIR}" --write-back
doctor-link schema validate "${PACKAGE_DIR}" --write --json >/dev/null
doctor-link handoff "${PACKAGE_DIR}" --tool codex --out "${REPORTS_DIR}/handoff"
doctor-link view "${PACKAGE_DIR}" --build-only

BEFORE=$(doctor-link diagnose before --project "E2E" --summary "before" --out "${REPORTS_DIR}" | awk -F': ' '/Created before package/ {print $2}')
AFTER=$(doctor-link diagnose after --project "E2E" --summary "after" --before-package "${BEFORE}" --out "${REPORTS_DIR}" | awk -F': ' '/Created after package/ {print $2}')
doctor-link diagnose compare "${AFTER}" --json >/dev/null
doctor-link diagnose verify "${AFTER}" --json >/dev/null
doctor-link schema validate "${AFTER}" --write --json >/dev/null
doctor-link health "${REPORTS_DIR}" --json >/dev/null

test -f "${PACKAGE_DIR}/doctor-report.json"
test -f "${PACKAGE_DIR}/verification-result.json"
test -f "${PACKAGE_DIR}/schema-validation-result.json"
test -f "${REPORTS_DIR}/handoff/handoff-manifest.json"
test -f "${PACKAGE_DIR}/.doctorlink-web/index.html"
test -f "${AFTER}/diagnosis-pipeline-summary.json"
test -f "${AFTER}/schema-validation-result.json"
test -f "${REPORTS_DIR}/project-health.json"

echo "Doctor link E2E validation passed: ${WORK_DIR}"
