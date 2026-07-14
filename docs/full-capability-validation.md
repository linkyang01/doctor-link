# Full Capability Validation

Doctor link maintains an installed-package validation lab at [`examples/full-capability-lab`](../examples/full-capability-lab/README.md). Its purpose is to prove that every public CLI route can execute in a coherent workflow, including expected failure behavior.

## Validation layers

| Layer | What is proven |
| --- | --- |
| Unit and regression tests | Function-level behavior, edge cases, and previously fixed defects. |
| Full capability inventory | The declared matrix exactly matches the live Click command tree. |
| Complex scenario runner | All 63 routes execute through 72 real subprocess invocations with isolated output. |
| Installed-wheel run | The built distribution, entrypoint, dependencies, examples, and runtime files work outside the source import path. |
| Cross-platform smoke | Core source installation and commands work on Ubuntu, macOS, and Windows. |

## Route groups

The matrix covers:

- workspace and discovery: `init`, `scan`, `plan`, `preflight`, `env`, `probe`;
- reporting and evidence: `report`, `legacy-report`, `ai-task`, `collect`, `assert`, `record`, `vly-proof`;
- automated diagnosis and repair: `strategy validate`, `reproduce list/run`, `test list/run`, `diagnose before/after/compare/verify`, `compare`, `verify`, `solve`;
- AI collaboration: `handoff list/check/generate`, `ai-result`, `diagnosis-history`, `assertion-check`, `risk-review`;
- local user experience: `view`, `workbench-note`, `home`, `wizard`, `diagnose-now`, `doctor-package`;
- standards and operations: `schema validate/migrate`, `conformance run`, `ci report`, `distribution check`, `health`;
- extension governance: `adapter list/validate/run`, `plugin list/validate/run`;
- privacy and integrity: `privacy scan/redaction-gate/export-gate`, `integrity manifest/verify`;
- knowledge and archive: `knowledge build/query/export`, `archive create/inspect/policy-check/export`;
- console version reporting: `--version`.

## Expected failures are first-class results

The lab does not turn known failures into shell success. Raw secret scans, unsafe export gates, and tampered integrity checks must return non-zero. The runner records those invocations as `expected_failure` only when the exit code and evidence match the scenario contract.

The six-bug service similarly succeeds at the scenario level only when its known application failures remain blocked from verification and AI handoff closure.

The automatic-solve fixture is a clean Git-backed Python project with a real duplicate-charge defect. The lab proves that Doctor link executes the failing checks and returns `approval_required` without invoking Codex or editing code, preserving the explicit repair boundary in an installed-wheel run.

A second automatic-solve fixture is a clean Git-backed Node.js project. The installed wheel must classify it as JavaScript, discover `npm test`, reproduce the failure, protect `package.json` and the original test, and stop at the same approval boundary. This adds language-specific proof without allowing the offline lab to call Codex.

Package export is exercised in both directions: raw secrets must be blocked by default, while a reviewed safe package exports with portable paths. A legacy export manifest must migrate with backups and without overwriting a formal package manifest.

## CI enforcement

The package job builds the wheel and source distribution, installs the wheel into a clean virtual environment, and runs the complete lab using that installed console entrypoint. CI uploads the full report and command logs for inspection.

`tests/test_full_capability_inventory.py` compares the live CLI command tree to the lab's `CAPABILITIES` set. Adding a command without a scenario therefore fails the normal test suite.

## Local command

```bash
python -m build
python examples/full-capability-lab/run-all.py --dist dist
```

The run is local-first. It requires Node.js and npm for the JavaScript solve fixture, creates temporary evidence, and executes only repository-owned fixtures, explicitly approved fixture Adapter/Plugin commands, and local Doctor link commands.
