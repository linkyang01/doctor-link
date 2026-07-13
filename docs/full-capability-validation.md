# Full Capability Validation

Doctor link maintains an installed-package validation lab at [`examples/full-capability-lab`](../examples/full-capability-lab/README.md). Its purpose is to prove that every public CLI route can execute in a coherent workflow, including expected failure behavior.

## Validation layers

| Layer | What is proven |
| --- | --- |
| Unit and regression tests | Function-level behavior, edge cases, and previously fixed defects. |
| Full capability inventory | The declared matrix exactly matches the live Click command tree. |
| Complex scenario runner | All 61 routes execute as real subprocesses with isolated output. |
| Installed-wheel run | The built distribution, entrypoint, dependencies, examples, and runtime files work outside the source import path. |
| Cross-platform smoke | Core source installation and commands work on Ubuntu, macOS, and Windows. |

## Route groups

The matrix covers:

- workspace and discovery: `init`, `scan`, `plan`, `preflight`, `env`, `probe`;
- reporting and evidence: `report`, `legacy-report`, `ai-task`, `collect`, `assert`, `record`, `vly-proof`;
- automated diagnosis: `strategy validate`, `reproduce list/run`, `test list/run`, `diagnose before/after/compare/verify`, `compare`, `verify`;
- AI collaboration: `handoff list/check/generate`, `ai-result`, `diagnosis-history`, `assertion-check`, `risk-review`;
- local user experience: `view`, `workbench-note`, `home`, `wizard`, `diagnose-now`, `doctor-package`;
- standards and operations: `schema validate`, `conformance run`, `ci report`, `distribution check`, `health`;
- extension governance: `adapter list/validate/run`, `plugin list/validate/run`;
- privacy and integrity: `privacy scan/redaction-gate/export-gate`, `integrity manifest/verify`;
- knowledge and archive: `knowledge build/query/export`, `archive create/inspect/policy-check/export`;
- console version reporting: `--version`.

## Expected failures are first-class results

The lab does not turn known failures into shell success. Raw secret scans, unsafe export gates, and tampered integrity checks must return non-zero. The runner records those invocations as `expected_failure` only when the exit code and evidence match the scenario contract.

The six-bug service similarly succeeds at the scenario level only when its known application failures remain blocked from verification and AI handoff closure.

## CI enforcement

The package job builds the wheel and source distribution, installs the wheel into a clean virtual environment, and runs the complete lab using that installed console entrypoint. CI uploads the full report and command logs for inspection.

`tests/test_full_capability_inventory.py` compares the live CLI command tree to the lab's `CAPABILITIES` set. Adding a command without a scenario therefore fails the normal test suite.

## Local command

```bash
python -m build
python examples/full-capability-lab/run-all.py --dist dist
```

The run is local-first. It creates temporary evidence and executes only repository-owned fixtures, explicitly approved fixture Adapter/Plugin commands, and local Doctor link commands.
