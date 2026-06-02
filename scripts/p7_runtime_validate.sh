#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "${1:-$(pwd)}" && pwd)"
WORK_DIR="${ROOT_DIR}/.doctorlink-p7-runtime"
REPORTS_DIR="${WORK_DIR}/DoctorReports"
LIB_DIR="${WORK_DIR}/VlyTestLibrary"
SAFE_DIR="${WORK_DIR}/safe-export"

rm -rf "${WORK_DIR}"
mkdir -p \
  "${LIB_DIR}/01-BasicFormats" \
  "${WORK_DIR}/logs" \
  "${SAFE_DIR}" \
  "${WORK_DIR}/.doctorlink/adapters/p7-adapter" \
  "${WORK_DIR}/.doctorlink/plugins/p7-plugin"

printf 'sample video placeholder\n' > "${LIB_DIR}/01-BasicFormats/sample.mp4"
printf 'subtitle placeholder\n' > "${LIB_DIR}/01-BasicFormats/sample.srt"
printf 'P7 runtime validation log\n' > "${WORK_DIR}/logs/p7.log"
printf 'safe export payload\n' > "${SAFE_DIR}/safe.txt"

cat > "${WORK_DIR}/.doctorlink/diagnosis.yml" <<'YAML'
diagnosis:
  project_type: p7-runtime-validation
  default_commands:
    - python --version
  evidence_rules:
    - collect local evidence only
  verification_rules:
    - run P7 runtime validation script
  excluded_paths:
    - .git
YAML

cat > "${WORK_DIR}/.doctorlink/reproduce.yml" <<'YAML'
reproductions:
  - id: p7-repro
    title: P7 reproduction
    kind: command
    command: python -c "print('repro-ok')"
    expected: repro-ok
YAML

cat > "${WORK_DIR}/.doctorlink/test-matrix.yml" <<'YAML'
jobs:
  - id: p7-test
    title: P7 runtime test
    command: python -c "print('test-ok')"
    required: true
YAML

cat > "${WORK_DIR}/.doctorlink/adapters/p7-adapter/adapter.yml" <<'YAML'
schema: doctor-link-adapter-v1
id: p7-adapter
name: P7 Adapter
version: 0.1.0
capabilities:
  - verification
commands:
  verification:
    - python
    - -c
    - "print('adapter-ok')"
YAML

cat > "${WORK_DIR}/.doctorlink/plugins/p7-plugin/plugin.yml" <<'YAML'
schema: doctor-link-plugin-v1
id: p7-plugin
name: P7 Plugin
version: 0.1.0
extension_points:
  - verification
permissions:
  - run_local_command
commands:
  verification:
    - python
    - -c
    - "print('plugin-ok')"
YAML

doctor-link strategy validate "${WORK_DIR}" --json > "${WORK_DIR}/strategy-validation.json"
doctor-link reproduce list "${WORK_DIR}" --json > "${WORK_DIR}/reproductions.json"
doctor-link test list "${WORK_DIR}" --json > "${WORK_DIR}/test-matrix.json"

doctor-link report "${LIB_DIR}" --out "${REPORTS_DIR}" >/dev/null
PACKAGE_DIR=$(find "${REPORTS_DIR}" -mindepth 1 -maxdepth 1 -type d | head -n 1)
test -n "${PACKAGE_DIR}"
test -f "${PACKAGE_DIR}/doctor-report.json"

doctor-link schema validate "${PACKAGE_DIR}" --write --json > "${WORK_DIR}/schema-initial.json"

ASSERTION_ID=$(doctor-link assert "${PACKAGE_DIR}" \
  --statement "P7 runtime validation should complete" \
  --expected "All P7 runtime commands complete" \
  --actual "P7 runtime validation is running" \
  --next-ai "Use P7 runtime evidence before closure" | awk -F': ' '/Added user assertion/ {print $2}')
test -n "${ASSERTION_ID}"

doctor-link collect "${PACKAGE_DIR}" \
  --project-root "${ROOT_DIR}" \
  --logs "${WORK_DIR}/logs/*.log" \
  --command "python --version" \
  --attachment "${SAFE_DIR}/safe.txt" \
  --note "P7 runtime validation evidence" >/dev/null

doctor-link reproduce run p7-repro "${WORK_DIR}" --package-dir "${PACKAGE_DIR}" --json > "${WORK_DIR}/reproduction-run.json"
doctor-link test run "${WORK_DIR}" --job p7-test --package-dir "${PACKAGE_DIR}" --json > "${WORK_DIR}/test-run.json"
doctor-link record "${PACKAGE_DIR}" \
  --name "P7 runtime validation" \
  --status passed \
  --expected "P7 runtime commands pass" \
  --actual "P7 runtime commands generated expected local outputs" \
  --assertion-id "${ASSERTION_ID}" >/dev/null

doctor-link ai-result "${PACKAGE_DIR}" \
  --summary "P7 runtime validation result" \
  --claimed-fix "Runtime validation evidence generated" \
  --assertion-id "${ASSERTION_ID}" \
  --verification-step "Run scripts/p7_runtime_validate.sh" \
  --tool generic >/dev/null
doctor-link diagnosis-history "${PACKAGE_DIR}" \
  --ai-pass "P7 runtime validation pass" \
  --user-correction "Require CI evidence before closure" \
  --verification-attempt "scripts/p7_runtime_validate.sh" \
  --tool generic >/dev/null
doctor-link assertion-check "${PACKAGE_DIR}" >/dev/null
doctor-link risk-review "${PACKAGE_DIR}" --file doctor_link/core/knowledge_archive.py --boundary doctor_link/ >/dev/null

doctor-link verify "${PACKAGE_DIR}" --write-back >/dev/null
doctor-link schema validate "${PACKAGE_DIR}" --write --json > "${WORK_DIR}/schema-final.json"
doctor-link handoff "${PACKAGE_DIR}" --tool generic --out "${WORK_DIR}/handoff" >/dev/null
doctor-link view "${PACKAGE_DIR}" --build-only >/dev/null
doctor-link workbench-note "${PACKAGE_DIR}" --note "P7 runtime validation note" --enable-write-back --json > "${WORK_DIR}/workbench-note.json"

doctor-link ci report "${REPORTS_DIR}" --out "${WORK_DIR}/ci" --json > "${WORK_DIR}/ci-report.json"

if [ ! -d "${ROOT_DIR}/dist" ] || [ -z "$(find "${ROOT_DIR}/dist" -name '*.whl' -print -quit 2>/dev/null)" ] || [ -z "$(find "${ROOT_DIR}/dist" -name '*.tar.gz' -print -quit 2>/dev/null)" ]; then
  (cd "${ROOT_DIR}" && python -m build >/dev/null)
fi

doctor-link distribution check "${ROOT_DIR}" --dist "${ROOT_DIR}/dist" --out "${WORK_DIR}/distribution" --json > "${WORK_DIR}/distribution.json"

doctor-link adapter list "${WORK_DIR}" --json > "${WORK_DIR}/adapter-list.json"
doctor-link adapter validate "${WORK_DIR}/.doctorlink/adapters/p7-adapter/adapter.yml" --json > "${WORK_DIR}/adapter-validate.json"
doctor-link adapter run p7-adapter verification "${WORK_DIR}" --out "${WORK_DIR}/adapters" --json > "${WORK_DIR}/adapter-run.json"

doctor-link plugin list "${WORK_DIR}" --json > "${WORK_DIR}/plugin-list.json"
doctor-link plugin validate "${WORK_DIR}/.doctorlink/plugins/p7-plugin/plugin.yml" --json > "${WORK_DIR}/plugin-validate.json"
doctor-link plugin run p7-plugin verification "${WORK_DIR}" --out "${WORK_DIR}/plugins" --json > "${WORK_DIR}/plugin-run.json"

doctor-link integrity manifest "${SAFE_DIR}" --out "${WORK_DIR}/integrity-manifest.json" --json > "${WORK_DIR}/integrity-manifest.stdout.json"
doctor-link integrity verify "${SAFE_DIR}" "${WORK_DIR}/integrity-manifest.json" --out "${WORK_DIR}/integrity-verify.json" --json > "${WORK_DIR}/integrity-verify.stdout.json"
doctor-link privacy scan "${SAFE_DIR}" --out "${WORK_DIR}/privacy-scan.json" --json > "${WORK_DIR}/privacy-scan.stdout.json"
doctor-link privacy redaction-gate "${SAFE_DIR}" --out "${WORK_DIR}/redaction-gate.json" --json > "${WORK_DIR}/redaction-gate.stdout.json"
doctor-link privacy export-gate "${SAFE_DIR}" --manifest "${WORK_DIR}/integrity-manifest.json" --out "${WORK_DIR}/export-gate.json" --json > "${WORK_DIR}/export-gate.stdout.json"

doctor-link knowledge build "${REPORTS_DIR}" --out "${WORK_DIR}/knowledge-index.json" --json > "${WORK_DIR}/knowledge-build.json"
doctor-link knowledge query "${WORK_DIR}/knowledge-index.json" "diagnostic" --json > "${WORK_DIR}/knowledge-query.json"
doctor-link knowledge export "${WORK_DIR}/knowledge-index.json" "${WORK_DIR}/knowledge-export.json" --json > "${WORK_DIR}/knowledge-export.stdout.json"

doctor-link archive create "${SAFE_DIR}" "${WORK_DIR}/archive" --metadata owner=p7 --json > "${WORK_DIR}/archive-create.json"
doctor-link archive inspect "${WORK_DIR}/archive" --json > "${WORK_DIR}/archive-inspect.json"
doctor-link archive policy-check "${WORK_DIR}/archive" --max-files 20 --json > "${WORK_DIR}/archive-policy.json"
doctor-link archive export "${WORK_DIR}/archive" "${WORK_DIR}/archive.zip" --json > "${WORK_DIR}/archive-export.json"

test -f "${WORK_DIR}/strategy-validation.json"
test -f "${WORK_DIR}/reproduction-run.json"
test -f "${WORK_DIR}/test-run.json"
test -f "${WORK_DIR}/ci/ci-report.json"
test -f "${WORK_DIR}/distribution/distribution-report.json"
test -f "${WORK_DIR}/adapters/p7-adapter-verification-run.json"
test -f "${WORK_DIR}/plugins/p7-plugin-verification-run.json"
test -f "${WORK_DIR}/integrity-verify.json"
test -f "${WORK_DIR}/privacy-scan.json"
test -f "${WORK_DIR}/redaction-gate.json"
test -f "${WORK_DIR}/export-gate.json"
test -f "${WORK_DIR}/knowledge-index.json"
test -f "${WORK_DIR}/knowledge-export.json"
test -f "${WORK_DIR}/archive/archive-record.json"
test -f "${WORK_DIR}/archive/archive-audit.jsonl"
test -f "${WORK_DIR}/archive.zip"
test -f "${PACKAGE_DIR}/.doctorlink-web/index.html"
test -f "${WORK_DIR}/handoff/handoff-manifest.json"

cat > "${WORK_DIR}/p7-runtime-validation-summary.md" <<'SUMMARY'
# Doctor link P7 Runtime Validation Summary

Result: success

The P7 runtime validation exercised evidence hardening outputs, workbench write-back, AI handoff runtime, operational automation, distribution readiness, adapter runtime, plugin runtime, integrity/privacy gates, local knowledge indexing, and local archive helpers.
SUMMARY

echo "Doctor link P7 runtime validation passed: ${WORK_DIR}"
