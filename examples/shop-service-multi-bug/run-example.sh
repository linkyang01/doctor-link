#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CASE_DIR="$ROOT_DIR/examples/shop-service-multi-bug"
OUT_DIR="${TMPDIR:-/tmp}/doctor-link-shop-multi-bug-$(date +%Y%m%d%H%M%S)"
HANDOFF_DIR="$OUT_DIR/handoff"
QUICK_DIR="$OUT_DIR/quick-report"

cd "$ROOT_DIR"

if ! command -v doctor-link >/dev/null 2>&1; then
  echo "doctor-link is not installed or not on PATH" >&2
  echo "Run: python -m pip install -e ." >&2
  exit 1
fi

echo "Doctor link shop-service-multi-bug example"
echo "Case: $CASE_DIR"
echo "Output: $OUT_DIR"
echo

echo "[1/10] strategy validate"
doctor-link strategy validate "$CASE_DIR" --json >/dev/null

echo "[2/10] reproduce all known issues"
for repro_id in repro-login-timeout repro-token-invalid repro-api-404 repro-order-no-inventory repro-db-pool repro-cache-ttl; do
  doctor-link reproduce run "$repro_id" "$CASE_DIR" --json >/dev/null
done

echo "[3/10] test matrix"
doctor-link test run "$CASE_DIR" --json >/dev/null

echo "[4/10] report"
doctor-link report "$CASE_DIR" --out "$OUT_DIR/DoctorReports" >/dev/null
PACKAGE_DIR="$(find "$OUT_DIR/DoctorReports" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
test -n "$PACKAGE_DIR"
test -f "$PACKAGE_DIR/doctor-report.json"

echo "[5/10] assertions"
doctor-link assert "$PACKAGE_DIR" --statement "P1: login timeout in auth.log" --severity critical --next-ai "Inspect src/auth/service.py TIMEOUT"
doctor-link assert "$PACKAGE_DIR" --statement "P3: GET /users/404 returns 500" --severity high --next-ai "Inspect src/api/routes.py get_user"
doctor-link assert "$PACKAGE_DIR" --statement "P5: DB pool exhausted after two connections" --severity critical --next-ai "Inspect src/db/pool.py release"
doctor-link assert "$PACKAGE_DIR" --statement "P6: cache TTL ignored and miss storm risk" --severity medium --next-ai "Inspect src/cache/client.py ttl handling"

echo "[6/10] ai result"
doctor-link ai-result "$PACKAGE_DIR" --tool cursor --summary "Identified auth, api, db, and cache defects" --claimed-fix "Adjust TIMEOUT, implement pool release, fix 404 mapping" >/dev/null

echo "[7/10] verify"
doctor-link verify "$PACKAGE_DIR" --write-back >/dev/null
test -f "$PACKAGE_DIR/verification-result.json"

echo "[8/10] workbench"
doctor-link view "$PACKAGE_DIR" --build-only >/dev/null
test -f "$PACKAGE_DIR/.doctorlink-web/index.html"

echo "[9/10] handoff"
doctor-link handoff "$PACKAGE_DIR" --tool cursor --out "$HANDOFF_DIR" >/dev/null
test -f "$HANDOFF_DIR/CURSOR_TASK.md"

echo "[10/10] diagnose-now"
doctor-link diagnose-now "$CASE_DIR" --report-json --output "$QUICK_DIR" >/dev/null
test -f "$QUICK_DIR/summary.md"

echo
echo "Example run completed successfully."
echo "Package: $PACKAGE_DIR"
echo "Workbench: $PACKAGE_DIR/.doctorlink-web/index.html"
echo "Handoff: $HANDOFF_DIR/CURSOR_TASK.md"
echo "Quick report: $QUICK_DIR/summary.md"