# Security Policy

Doctor link processes diagnostic evidence and can execute explicitly configured local commands. Security decisions therefore focus on command boundaries, sensitive-data handling, package integrity, and dependency hygiene.

## Supported versions

Doctor link is pre-1.0 software. Security fixes are applied to the current `main` branch and included in the next explicitly authorized release.

| Version | Status |
| --- | --- |
| Current `main` | Supported |
| Latest published GitHub Release | Best-effort support until replaced |
| Older tags and development snapshots | Not supported |

The source version may be newer than the latest published release. Check `pyproject.toml`, [project status](docs/project-status.md), and GitHub Releases separately.

## Reporting a vulnerability

Do not publish secrets, private diagnostic packages, exploit details, customer data, or unredacted logs in a public issue.

Preferred process:

1. Use GitHub private vulnerability reporting for `linkyang01/doctor-link` when available.
2. Include the affected command or component, the smallest safe reproduction, impact, and affected version or commit.
3. State whether an untrusted repository, `.doctorlink/` configuration, diagnostic package, adapter, or plugin is involved.
4. Remove tokens, credentials, email addresses, filesystem secrets, and private source content.
5. If private reporting is unavailable, open a minimal public issue requesting a private contact channel without vulnerability details.

Maintainers should acknowledge a complete report, reproduce it safely, assess severity, prepare a private fix when needed, and disclose only after a remediation path exists.

## Security model

Doctor link assumes:

- the local machine and Python environment are controlled by the user;
- repositories and diagnostic packages may contain untrusted or sensitive content;
- `.doctorlink/` configuration must be reviewed before command execution;
- generated reports remain local unless a user intentionally shares or uploads them;
- an AI-generated claim is not proof that a vulnerability or defect is fixed.

Doctor link is not a sandbox, endpoint-protection product, secret manager, hosted isolation service, or replacement for operating-system permissions.

## Local command execution boundary

Configured diagnostic, reproduction, and test-matrix commands are parsed into argument vectors and run without a shell. The safe runner:

- accepts normal quoted arguments;
- permits sequential `&&` segments;
- rejects pipelines, redirection, command substitution, and other shell control operators;
- records return code, stdout, stderr, duration, timeout, working directory, and executable metadata;
- resolves a missing cross-platform `python` alias to the active Doctor link interpreter.

Adapter and plugin commands are dry-run by default. Actual execution requires explicit `--allow-run`, manifest validation, declared capability or extension point, and the appropriate permission.

Review commands before approving execution. Do not run adapters, plugins, or configuration from an untrusted repository merely because validation succeeds.

## Diagnostic data handling

Diagnostic packages may contain:

- file paths and environment metadata;
- logs and command output;
- user assertions and issue descriptions;
- attachments and media metadata;
- project names, source excerpts, or test failures.

Before sharing a package:

1. run the configured redaction and privacy checks;
2. inspect `redaction-report.md` and relevant evidence files;
3. remove unnecessary attachments;
4. verify the integrity manifest when one is supplied;
5. use the privacy export gate;
6. share through an approved destination only.

Never rely on automatic redaction as the sole review step for regulated, customer-confidential, or credential-bearing data.

## Dependency and source checks

The repository CI runs:

- Ruff static checks;
- Bandit medium/high-confidence source scanning;
- `pip-audit` dependency vulnerability checks;
- tests with branch-aware coverage;
- wheel and source-distribution content validation;
- isolated wheel installation and dependency consistency checks.

Dependabot monitors GitHub Actions and Python dependencies. A passing scan reduces known risk but does not prove the absence of vulnerabilities.

## Release integrity

- Release tags are immutable; an existing tag must not be moved.
- The release workflow validates the requested tag against `pyproject.toml`.
- Wheel and sdist contents and Twine metadata must pass before release assets are created.
- Publishing requires explicit authorization.
- PyPI upload is optional and requires the configured repository secret.

## Out of scope

The project does not currently claim hosted isolation, production key management, artifact signing infrastructure, remote access control, cloud secret storage, or guaranteed detection of all malicious code.
