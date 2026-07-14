# Security Policy

Doctor link processes diagnostic evidence and can execute explicitly configured local commands. Security decisions therefore focus on command boundaries, sensitive-data handling, package integrity, and dependency hygiene.

## Supported versions

Security fixes are applied to the current `main` branch and included in the next explicitly authorized release. The latest published release receives best-effort support until replaced; older releases and development snapshots are not supported. Users should reproduce a report on the latest version before reporting unless upgrading is the problem.

## Reporting a vulnerability

Do not place secrets, access tokens, private source code, unredacted diagnostic packages, or exploitable vulnerability details in a public Issue.

Use [GitHub private vulnerability reporting](https://github.com/linkyang01/doctor-link/security/advisories/new) for suspected vulnerabilities. Include the affected command or component, version or commit, operating system, minimal safe reproduction, impact, and whether an untrusted repository, configuration, diagnostic package, adapter, or plugin is involved. If the private reporting form is unavailable, open a public Issue containing no sensitive or exploit-enabling detail and request a private contact channel.

The project will acknowledge a valid report, assess severity and affected versions, prepare a fix and regression test, and publish coordinated release information. Exact response times are not guaranteed while the project is maintained without a commercial support agreement.

## Scope

Security reports include secret leakage, unsafe archive paths, integrity or privacy-gate bypasses, command-execution boundary failures, permission bypasses, and malicious diagnostic-package handling. Ordinary bugs and feature requests should use the public Issue templates.

## Security model

Doctor link assumes that the local machine and Python environment are controlled by the user, while repositories and diagnostic packages may contain untrusted or sensitive content. Configuration must be reviewed before command execution. Generated reports remain local unless the user intentionally shares them, and an AI-generated claim is not proof that a vulnerability or defect is fixed.

Doctor link is not a sandbox, endpoint-protection product, secret manager, hosted isolation service, or replacement for operating-system permissions.

## Local command execution boundary

Configured diagnostic, reproduction, and test-matrix commands are parsed into argument vectors and run without a shell. The safe runner accepts normal quoted arguments and permitted sequential segments, rejects pipelines, redirection, command substitution, and other shell control operators, and records execution metadata. Adapter and plugin commands are dry-run by default; actual execution requires explicit permission and validated declarations.

Review commands before approving execution. Do not run adapters, plugins, or configuration from an untrusted repository merely because validation succeeds.

## Diagnostic data handling

Diagnostic packages may contain paths, environment metadata, logs, command output, assertions, issue descriptions, attachments, media metadata, source excerpts, or test failures. Before sharing a package:

1. run redaction and privacy checks;
2. inspect the redaction report and evidence files;
3. remove unnecessary attachments;
4. verify integrity when a manifest is supplied;
5. use the privacy export gate;
6. share only through an approved destination.

Never rely on automatic redaction as the sole review step for regulated, customer-confidential, or credential-bearing data.

## Dependency and source checks

CI runs Ruff, Bandit, dependency auditing, branch-aware coverage, distribution-content checks, Twine metadata validation, and isolated wheel installation. Dependabot monitors GitHub Actions and Python dependencies. Passing scans reduce known risk but do not prove the absence of vulnerabilities.

## Release integrity

- Release tags are immutable and must not be moved.
- Release workflows validate versions, contents, metadata, and installed wheels.
- Publishing requires explicit authorization.
- PyPI publication uses protected-environment Trusted Publishing with short-lived credentials and attestations.

## Out of scope

The project does not claim hosted isolation, production key management, remote access control, cloud secret storage, regulatory certification, or guaranteed detection of all malicious code.
