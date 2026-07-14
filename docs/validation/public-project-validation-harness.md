# Public-project validation harness

Status date: 2026-07-14

## Purpose

Provide a pinned, repeatable check that Doctor link can inspect representative public Python and JavaScript projects without expanding product scope. This closes the post-release validation gap tracked in Issue [#156](https://github.com/linkyang01/doctor-link/issues/156).

## Location

| Path | Role |
| --- | --- |
| `examples/public-project-validation/projects.json` | Pinned project set (URL, ref, full commit SHA) |
| `examples/public-project-validation/README.md` | Operator notes |
| `scripts/validate_public_projects.py` | Clone, commit-pin check, read-only `preflight --json` |
| `tests/test_public_project_validation.py` | Offline tests that the manifest is pinned and multi-language |
| `.github/workflows/post-release-smoke.yml` | Scheduled/public PyPI install smoke (separate from this harness) |

## Current pin set

Six projects: three Python (`click`, `requests`, `pydantic`) and three JavaScript (`p-limit`, `chalk`, `axios`). Each entry requires a 40-character commit SHA so drift is detectable.

## How to run

```bash
python -m pip install -e '.[dev]'
python scripts/validate_public_projects.py --out DoctorReports/public-project-validation
```

The runner clones into a temporary workspace, verifies HEAD equals the pinned commit, runs `doctor-link preflight --json`, and writes `results.json` plus a short markdown summary under `--out`.

## Evidence recorded in this PR

- Harness code, pinned manifest, offline unit test, and operator docs are present.
- Live run on 2026-07-14: **6/6 PASS** (commit-pinned clone + read-only preflight, warnings allowed, zero blockers). Results: [`docs/validation/evidence/public-project-validation-2026-07-14/`](evidence/public-project-validation-2026-07-14/).
- External real-project exercise on `pallets/click` (Issue #156 comments) already validated assist/solve verification contracts; usability fixes from that feedback are included in the same change set.

## Non-goals

This harness does **not** authorize automatic repair against public repositories, invoke Codex, or claim product support for third-party project internals. It only revalidates Doctor link preflight readiness on known public trees.
