# JavaScript/TypeScript Automatic Solve Validation

- Validation date: 2026-07-13
- Released version: `0.3.0`
- Status: expanded local, Python 3.10–3.14 cloud, final-head, and GitHub Release validation passed

## Scope

This validation proves that `doctor-link solve` can apply the same bounded repair contract used for Python projects to a Node.js JavaScript/TypeScript repository:

1. detect the project language without claiming generic all-language support;
2. discover the project-owned test command;
3. reproduce a real failure before any edit;
4. require explicit repair approval;
5. isolate changes on a repair branch;
6. protect the acceptance contract with file hashes;
7. bound Codex to at most three repair rounds;
8. independently rerun every required check;
9. return `verified` only when checks pass and protected inputs remain unchanged.

## Implemented language behavior

- `package.json` or JavaScript/TypeScript files under common source roots identify a Node.js project.
- A non-placeholder `scripts.test` selects the package manager from `packageManager` first, then pnpm, Yarn, or Bun lockfiles, with npm as the default.
- JavaScript `.test.*` and `.spec.*` files fall back to `node --test` when no usable package test script exists.
- Generated dependencies, caches, builds, and coverage directories are pruned from verification discovery.
- Package manifests, lockfiles, workspace configuration, TypeScript/JavaScript configuration, tests, and common Jest, Vitest, Playwright, and Cypress configuration files are protected.
- A missing required executable or timed-out required baseline check blocks before repair branch creation and before Codex invocation.

## Automated regression evidence

The repository suite passed `339` tests with `85.48%` branch-aware coverage and an enforced `85%` floor. JavaScript/TypeScript-specific regressions prove:

- JavaScript and TypeScript source detection;
- npm default discovery and pnpm/Yarn selection from metadata or lockfiles;
- `node --test` fallback;
- real npm execution with independent verification;
- Windows package-manager launcher resolution without weakening the shell-free command boundary;
- two-round repair where the first partial fix remains failed and the second completes the contract;
- test-file tampering blocked before verification;
- package test-script weakening blocked before verification;
- package-lock and test-runner configuration weakening blocked before verification while generated `node_modules` content remains excluded;
- missing verification tooling blocked before repair;
- baseline timeout blocked before repair.

The installed-wheel full-capability lab passed all `63/63` public routes through `72` real command invocations and ten scenario invariants. Its Node.js approval-gate fixture must be detected as JavaScript, select `npm test`, protect `package.json` and the original test, reproduce the defect, and stop at `approval_required` without editing code.

## Live Codex repair

A disposable Git-backed Node.js inventory library was built with three acceptance tests:

- repeated successful reservation is idempotent;
- insufficient stock is rejected atomically and the same request can be retried after replenishment;
- invalid quantities and unknown products fail without mutating stock or the processed-request set.

The broken implementation mutated stock and recorded the request before validating availability or input. The installed candidate wheel produced this sequence:

| Stage | Result |
| --- | --- |
| Project detection | `javascript` |
| Discovered command | `npm test` |
| Baseline | 1 passed, 2 failed |
| Preview without approval | `approval_required`, no branch or edit |
| Authorized repair | isolated `doctor-link/solve-*` branch |
| Codex rounds | 1 |
| Changed production files | `inventory.js` only |
| Independent verification | 3 passed, 0 failed |
| Protected-input changes | none |
| Final status | `verified` |

The protected hashes were identical before and after repair:

| Protected input | SHA-256 |
| --- | --- |
| `package.json` | `685afcc76cd102ae3ccff476fb1f30b6421b61f5227facfefe513ced2b02a90a` |
| `tests/inventory.test.js` | `3f90d9b391ea9953112f0c2a74916e419d826e0b8328b206332de78e34d433f5` |

## Repository quality gates

| Gate | Local result |
| --- | ---: |
| Full tests | 339 passed |
| Branch-aware coverage | 85.48% |
| Ruff | passed |
| Bandit medium/high | 0 findings |
| Dependency audit | 0 known third-party vulnerabilities |
| Wheel and sdist build | passed |
| Distribution contents | passed |
| Twine metadata | passed |
| Isolated wheel install | passed |
| Project validation | passed |
| Self-validation | passed |
| E2E validation | passed |
| P7 runtime validation | passed |
| Installed-wheel capability lab | 63/63 routes, 72 invocations, 10 scenarios |

## Cloud validation

[GitHub Actions run `29263187097`](https://github.com/linkyang01/doctor-link/actions/runs/29263187097) validated code commit `c9426e7` on PR `#147`. All ten jobs passed:

- Python 3.10, 3.11, 3.12, 3.13, and 3.14;
- security checks;
- wheel build and installed-package capability validation;
- Ubuntu JavaScript solve smoke validation;
- macOS JavaScript solve smoke validation;
- Windows JavaScript solve smoke validation.

The Windows job directly exercised the real npm repair and verification-input protection cases that exposed the original launcher-resolution defect.

Final PR head `45f3d52` passed the same ten-job matrix in [run `29299016223`](https://github.com/linkyang01/doctor-link/actions/runs/29299016223). PR `#147` merged as `e0224cc`, and [release workflow `29299367180`](https://github.com/linkyang01/doctor-link/actions/runs/29299367180) rebuilt, installed, and validated the distributions before publishing [GitHub Release `v0.3.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.3.0). PyPI publication was disabled.

## Honest limits

- The live repair used Node.js `26.0.0`, npm `11.12.1`, and the existing authenticated Codex CLI.
- npm and `node --test` executed locally. pnpm, Yarn, and Bun selection is covered by automated discovery regressions but was not runtime-tested locally because those executables were not all installed.
- TypeScript is detected and its project test command can be executed, but Doctor link does not transpile TypeScript or install a runner; the repository must provide its own working toolchain.
- Mixed-language monorepos should run from the target package root and use explicit commands when root-level discovery is ambiguous.
- The release evidence certifies only the named commits, artifacts, and configured CI environments, not arbitrary customer or production environments.
