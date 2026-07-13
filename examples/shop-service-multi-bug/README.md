# Shop Service Multi-Bug Example

Simulated e-commerce backend with six known issues across auth, API, database, and cache subsystems.

This example is designed for Doctor link workflow testing: multi-problem reproduction, assertions, verification, local workbench, and AI handoff.

## Known issues

| ID | Subsystem | Problem |
|----|-----------|---------|
| P1 | auth | Login always times out (`TIMEOUT=0.001`) |
| P2 | auth | Expired token validation gap |
| P3 | api | Missing user returns `500` instead of `404` |
| P4 | api | Order created without inventory check |
| P5 | db | Connection pool exhausted; `release()` is a no-op |
| P6 | cache | TTL ignored; cache miss storm risk |

## Layout

```text
examples/shop-service-multi-bug/
├── README.md
├── run-example.sh
├── config/app.yml
├── logs/
│   ├── auth.log
│   ├── api.log
│   ├── db.log
│   └── cache.log
├── src/
│   ├── auth/service.py
│   ├── api/routes.py
│   ├── db/pool.py
│   └── cache/client.py
├── tests/
│   ├── unit/
│   └── integration/
└── .doctorlink/
    ├── diagnosis.yml
    ├── reproduce.yml
    └── test-matrix.yml
```

## One-click test

From the repository root:

```bash
bash examples/shop-service-multi-bug/run-example.sh
```

The script first creates a diagnostic package, then records four human assertions and attaches every reproduction/test result to that package. Its final exit code is 0 only when the scenario itself was validated: the known database failures must return non-zero, verification must remain blocked, and the generated handoff must say `needs_repair`. It does **not** claim the six example defects were fixed.

## Manual commands

```bash
doctor-link strategy validate examples/shop-service-multi-bug --json
doctor-link reproduce list examples/shop-service-multi-bug --json
doctor-link report examples/shop-service-multi-bug --out /tmp/shop-multi-bug-reports
```

After generating a package:

```bash
PACKAGE_DIR=$(find /tmp/shop-multi-bug-reports -mindepth 1 -maxdepth 1 -type d | head -n 1)
doctor-link assert "$PACKAGE_DIR" --statement "P1: login timeout in auth.log" --severity critical
doctor-link reproduce run repro-login-timeout examples/shop-service-multi-bug --package-dir "$PACKAGE_DIR" --json
doctor-link test run examples/shop-service-multi-bug --package-dir "$PACKAGE_DIR" --json
doctor-link verify "$PACKAGE_DIR" --write-back
doctor-link view "$PACKAGE_DIR" --build-only
doctor-link handoff "$PACKAGE_DIR" --tool cursor --out /tmp/shop-multi-bug-handoff
doctor-link diagnose-now examples/shop-service-multi-bug --report-json --output /tmp/shop-multi-bug-quick
```

## Expected behavior

- Reproduction `repro-db-pool` should fail on the third connection acquire.
- Test matrix job `test-pool-exhaust` should fail for the same reason.
- Both failing commands return exit code 1 after emitting parseable JSON.
- The configured assertion statements link P1, P3, P5, and P6 to their automated evidence records.
- Verification reports `not_verified`, includes the database checks as blockers/reruns, and does not claim closure.
- Handoff compatibility reports `needs_repair` with `verification_status: not_verified`.
- The example is local-only and does not publish or upload anything.
