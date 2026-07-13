# Doctor link Local Quality Scorecard

Assessment date: 2026-07-13
Assessed source: local repaired `0.1.2` release candidate
Result: **92/100 — exceeds the 90-point local-readiness target**

This score measures repository-side completeness and local release readiness. It does not certify an unpublished Git commit, a GitHub Release, PyPI publication, or cloud execution that has not happened.

## Scoring

| Area | Weight | Score | Evidence |
| --- | ---: | ---: | --- |
| Functional completeness | 30 | 28 | Four official end-to-end validation paths pass; repaired CLI, evidence, verification, handoff, workbench, adapter, plugin, privacy, archive, and distribution flows are exercised. |
| Reliability and tests | 20 | 18 | 273 tests pass; branch-aware coverage is 85.09%; coverage has an enforced 85% floor. |
| Security and privacy | 20 | 19 | Shell-free configured command execution, explicit adapter/plugin approval, Bandit with zero medium/high findings, dependency audit with zero known vulnerabilities, privacy/export gates, and Dependabot. |
| Packaging and installation | 15 | 14 | Wheel and sdist build; content gate and Twine pass; isolated wheel install, dependency check, version check, and preflight pass. |
| Documentation and maintainability | 10 | 9 | Changelog, security policy, installation, release boundaries, validation docs, CI gates, and release checks are aligned with the repaired state. |
| Portability and operations | 5 | 4 | Portable Python command resolution and Linux/macOS/Windows CI smoke jobs are present; current repaired commit still awaits cloud execution. |
| **Total** | **100** | **92** | **Local readiness target passed.** |

## Current validation receipts

- `273 passed`
- branch-aware coverage: `85.09%`
- Ruff: passed
- Bandit medium/high findings: `0`
- third-party dependency vulnerabilities: `0 known`
- wheel/sdist content validation: passed
- Twine package validation: passed
- isolated wheel dependency check: passed
- `doctor-link preflight`: 7 checks passed, 0 blockers, 0 warnings
- official E2E, self-validation, project validation, and P7 runtime validation: passed

## Remaining certification gap

The local score is intentionally capped below full marks because the current repaired commit has not yet been pushed and run through the configured Linux, macOS, Windows, Python 3.10, Python 3.11, and Python 3.12 cloud matrix. Publication also requires explicit authorization.
