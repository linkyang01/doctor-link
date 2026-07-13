# Contributing to Doctor link

Thank you for improving Doctor link. Contributions should preserve its evidence-first, local-first, privacy-aware diagnostic model.

## Contribution principles

- Start from a reproducible problem or a clearly described product need.
- Preserve human-confirmed assertions; do not let generated conclusions silently override them.
- Add verification evidence before claiming closure.
- Keep command execution shell-free unless a separately reviewed design explicitly changes that boundary.
- Avoid unrelated refactors in a bug-fix pull request.
- Keep documentation, examples, schemas, and CLI behavior aligned.
- Never publish releases, tags, or packages without explicit authorization.

## Development requirements

- Git
- Python 3.10, 3.11, or 3.12
- A virtual environment

Set up the repository:

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
doctor-link preflight . --json
```

Windows PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Branch and commit workflow

1. Start from an up-to-date `main` branch.
2. Create a focused branch such as `fix/verification-writeback` or `feature/preflight-check`.
3. Make the smallest coherent change that resolves the issue.
4. Add or update tests and documentation.
5. Run the relevant local gates.
6. Open a pull request using the repository template.

Commit messages should be short, imperative, and scoped to the outcome, for example:

```text
fix verification evidence aliases
add cross-platform preflight checks
document release authorization boundary
```

## Required validation

For documentation-only changes:

```bash
git diff --check
pytest -q
```

For runtime changes:

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-branch --cov-fail-under=85
```

For command execution, security, dependency, packaging, or release changes, also run:

```bash
bandit -r doctor_link -ll
pip-audit
python -m build
python scripts/validate_distribution_contents.py dist
python -m twine check dist/*
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

## Test expectations

- Every bug fix should include a regression test that fails without the fix.
- New CLI options should cover successful use, invalid input, and machine-readable output when supported.
- Command runners must test unsafe operator rejection and missing-executable behavior.
- Packaging changes should test metadata and distribution contents.
- Keep branch-aware coverage at or above the configured 85% floor.
- Do not weaken or bypass a quality gate merely to make CI green.

## Documentation expectations

Update documentation whenever a change affects:

- installation or supported Python versions;
- CLI commands, options, defaults, aliases, or output formats;
- `.doctorlink/` configuration;
- diagnostic package fields or schemas;
- security, privacy, redaction, or execution boundaries;
- GitHub Actions, release checks, or supported environments;
- version and publication status.

At minimum, review the root `README.md`, the relevant guide under `docs/`, both language README files, `CHANGELOG.md`, and validation/release documents.

## Pull request expectations

A pull request should explain:

- the problem and root cause;
- what changed and why;
- user and developer impact;
- files or interfaces affected;
- tests and validation performed;
- security or privacy implications;
- known limitations and follow-up work;
- whether the change affects release readiness.

Attach safe logs or report excerpts when useful. Never attach secrets, tokens, customer data, private source, or an unredacted diagnostic package.

## GitHub Actions behavior

PRs targeting `main` run:

- Python 3.10, 3.11, and 3.12 test jobs;
- Ruff and branch-aware coverage;
- CLI, E2E, and P7 runtime validation;
- package build, content inspection, Twine, and isolated wheel installation;
- Bandit and dependency vulnerability checks;
- Ubuntu, macOS, and Windows smoke jobs.

All required jobs should pass before a PR is marked ready for review. See [GitHub repository guide](docs/github-repository-guide.md).

## Security reports

Do not open a public issue containing exploit details or sensitive evidence. Follow [SECURITY.md](SECURITY.md) and use GitHub private vulnerability reporting when available.

## Release boundary

Contributors may prepare version changes, release notes, checklists, and artifacts in a PR. They must stop before:

- creating or moving a public release tag;
- creating a GitHub Release;
- uploading release assets;
- publishing to PyPI or another registry.

Those actions require explicit authorization and a successful release workflow.
