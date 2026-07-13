# Doctor link Validation Evidence Index

This index separates current repaired-source evidence, historical evidence, and actions that have not occurred. A green workflow run certifies only the commit and scope named below.

## Current repaired-source certification

- Repository: `linkyang01/doctor-link`
- Pull request: [#134 Harden Doctor link release readiness](https://github.com/linkyang01/doctor-link/pull/134)
- Implementation commit: `4e46a88d363250915ce625dbd58dceadc8ab7c4c`
- 100-point certification commit: `8798b9af8e044431e370af83f5929a67f5361d48`
- Implementation run: [29221790817](https://github.com/linkyang01/doctor-link/actions/runs/29221790817)
- 100-point certification run: [29221918410](https://github.com/linkyang01/doctor-link/actions/runs/29221918410)
- Final documentation CI run: [29223178425](https://github.com/linkyang01/doctor-link/actions/runs/29223178425)
- Merge commit: `862281f38af6550a149a45fbf002560302e6423b`
- Release workflow: [29223309411](https://github.com/linkyang01/doctor-link/actions/runs/29223309411)
- Published release: [v0.1.2](https://github.com/linkyang01/doctor-link/releases/tag/v0.1.2)
- Conclusion: `success`
- Date: 2026-07-13

## Final cloud jobs

| Job | Environment | Result |
| --- | --- | ---: |
| Python 3.10 | Ubuntu | Passed |
| Python 3.11 | Ubuntu | Passed |
| Python 3.12 | Ubuntu | Passed |
| Security checks | Ubuntu / Python 3.12 | Passed |
| Build and install wheel | Ubuntu / Python 3.12 | Passed |
| Cross-platform smoke | Ubuntu / Python 3.12 | Passed |
| Cross-platform smoke | macOS / Python 3.12 | Passed |
| Cross-platform smoke | Windows / Python 3.12 | Passed |

## Validated gates

The current CI evidence covers:

- editable installation with declared development dependencies;
- dependency consistency through `pip check`;
- Ruff static checks;
- 273 automated tests;
- 85.09% branch-aware coverage with an 85% minimum;
- CLI entrypoint and diagnostic smoke flows;
- strategy and read-only preflight validation;
- E2E validation;
- P7 runtime validation;
- wheel and source-distribution build;
- required/forbidden distribution content inspection;
- Twine metadata validation;
- isolated wheel installation;
- Bandit source scan with zero medium/high findings;
- dependency audit with zero known third-party vulnerabilities;
- Ubuntu, macOS, and Windows portability smoke checks.

## Local validation receipts

Current local repaired-source validation on macOS/Python 3.12 includes:

| Check | Result |
| --- | ---: |
| Full regression suite | 273 passed |
| Branch-aware coverage | 85.09% |
| Ruff | Passed |
| Bandit medium/high | 0 findings |
| Dependency vulnerabilities | 0 known |
| Wheel and sdist content | Passed |
| Twine | Passed |
| Isolated wheel install | Passed |
| Preflight | 7 passed, 0 warnings, 0 blockers |
| E2E validation | Passed |
| Project validation | Passed |
| Self-validation | Passed |
| P7 runtime validation | Passed |

Representative commands:

```bash
python -m pip install -e '.[dev]'
doctor-link preflight . --json
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-branch --cov-fail-under=85
bandit -r doctor_link -ll
pip-audit
python -m build
python scripts/validate_distribution_contents.py dist
python -m twine check dist/*
bash scripts/validate_doctor_link.sh DoctorLinkValidation
bash scripts/self_validate_doctor_link.sh DoctorLinkSelfValidation
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

## Artifact interpretation

- `coverage.xml` is machine-readable test coverage evidence.
- `dist/*.whl` and `dist/*.tar.gz` are build outputs, not proof of publication.
- `.doctorlink-e2e/` and `.doctorlink-p7-runtime/` contain runtime validation evidence.
- `DoctorReports/` contains generated diagnostic packages and project health records.
- Actions artifacts are temporary CI outputs and may expire under repository retention settings.

Artifacts may contain project-sensitive data. Review privacy and redaction output before sharing them.

## Published release evidence

GitHub Release `v0.1.2` was published on 2026-07-13. Its annotated tag resolves to merge commit `862281f38af6550a149a45fbf002560302e6423b`.

| Asset | Size | SHA-256 |
| --- | ---: | --- |
| `doctor_link-0.1.2-py3-none-any.whl` | 150,053 bytes | `9df6283381a8facabb0938d33180db63dffc41bbb31c04e5120bc340cb619bae` |
| `doctor_link-0.1.2.tar.gz` | 309,134 bytes | `0badcdd229e6a2a01e1551485655cef844447ad808697804838ab87aaba66eb8` |

Both downloaded release assets passed Twine metadata validation. PyPI publication was disabled in the release workflow and was not performed.

## Historical evidence

An earlier repository-root-cleanup validation was recorded for PR `#110`, merge commit `09830b934d92c41509daa75b929d82081c6c827d`, CI run `#312`, with a successful result. It remains historical evidence and must not replace the current repaired-source runs above.

The earlier local Mac record at `docs/p5.10-local-validation.md` covers commit `14b552c24feff1f2e28a8cb68e352e9d5b0c76af`, Python 3.11.15, 217 tests, and 84% coverage. It also remains historical.

## Certification limits

Current evidence proves the defined repository validation matrix. It does not prove:

- PyPI availability;
- customer-environment or production acceptance;
- hosted platform, account, telemetry, marketplace, signing-key, archive, knowledge-base, or RBAC capabilities.

See [cloud validation certificate](cloud-validation-certificate.md), [100-point scorecard](local-quality-scorecard.md), and [release candidate checklist](release-candidate-checklist.md).
