# Doctor link Local Quality Scorecard

Assessment date: 2026-07-13
Assessed source: `0.1.3` release candidate commit `4119f0e`, later published from merge commit `fa779da`
Result: **100/100 — repository release-readiness target completed**

This score measures the defined repository-side release-readiness rubric. It does not mean the software has no possible future improvements, and it does not claim PyPI publication, customer-environment acceptance, or production deployment. GitHub Release `v0.1.3` was published after the score was revalidated.

## Scoring

| Area | Weight | Score | Evidence |
| --- | ---: | ---: | --- |
| Functional completeness | 30 | 30 | Four official end-to-end validation paths pass on the repaired source; CLI, evidence, verification, handoff, workbench, adapter, plugin, privacy, archive, and distribution flows are exercised. |
| Reliability and tests | 20 | 20 | 298 tests pass with 85.25% branch-aware coverage and an enforced 85% floor across Python 3.10, 3.11, and 3.12 cloud jobs; 62/62 public routes pass through 70 installed-package invocations and eight complex scenarios. |
| Security and privacy | 20 | 20 | Shell-free configured commands, explicit adapter/plugin approval, zero medium/high Bandit findings, zero known dependency vulnerabilities, privacy/export gates, and a successful cloud security job. |
| Packaging and installation | 15 | 15 | Wheel and sdist build, content gate, Twine, isolated wheel install, dependency check, CLI smoke, and preflight all pass locally and in the cloud package job. |
| Documentation and maintainability | 10 | 10 | Changelog, security policy, installation, release boundaries, validation evidence, CI gates, and release checks are aligned with the repaired state. |
| Portability and operations | 5 | 5 | Portable Python resolution and real GitHub-hosted Ubuntu, macOS, and Windows smoke jobs pass. |
| **Total** | **100** | **100** | **Defined repository release-readiness rubric completed.** |

## Current validation receipts

- `298 passed`
- branch-aware coverage: `85.25%`
- Ruff: passed
- Bandit medium/high findings: `0`
- third-party dependency vulnerabilities: `0 known`
- wheel/sdist content validation: passed
- Twine package validation: passed
- isolated wheel dependency check: passed
- `doctor-link preflight`: 7 checks passed, 0 blockers, 0 warnings
- official E2E, self-validation, project validation, and P7 runtime validation: passed
- full capability lab: `62/62` public routes, `70` real invocations, `8` complex scenarios
- GitHub Actions run [`29245883700`](https://github.com/linkyang01/doctor-link/actions/runs/29245883700): passed
- cloud jobs: Python 3.10, 3.11, 3.12, security, package install, Ubuntu, macOS, and Windows all passed

## Certification boundary

The release candidate commit passed the complete configured cloud matrix in PR `#140`. The PR was later merged as commit `fa779da`; after explicit authorization, [GitHub Release `v0.1.3`](https://github.com/linkyang01/doctor-link/releases/tag/v0.1.3) was published by workflow `29246045227`. PyPI publication was disabled and not performed.
