# Security Policy

## Supported version

Doctor link is pre-1.0 software. Security fixes are applied to the current
`main` branch and included in the next explicitly authorized release.

## Reporting a vulnerability

Do not publish secrets, private diagnostic packages, or exploit details in a
public issue. Use GitHub's private vulnerability reporting feature for this
repository when it is available. Otherwise, open a minimal public issue asking
the maintainer for a private contact channel without including sensitive data.

Include the affected command, the smallest safe reproduction, expected impact,
and whether untrusted repository configuration is involved.

## Local command execution boundary

Doctor link can run configured diagnostic, reproduction, test, adapter, and
plugin commands. Review `.doctorlink/` configuration before running commands
from an untrusted repository. Reproduction and test-matrix commands execute as
argument vectors without a shell; shell pipelines, redirections, and command
substitution are intentionally unsupported. Adapter and plugin execution also
requires explicit `--allow-run` approval.
