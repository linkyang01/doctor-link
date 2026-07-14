# Doctor link Full Capability Lab

This lab runs every Doctor link CLI capability through realistic local scenarios. It is an executable validation asset, not a list of help commands.

## Coverage contract

- 68/68 capability routes, including the version entrypoint;
- at least one real process execution for every route;
- successful and expected-blocked outcomes checked separately;
- machine-readable per-command logs and a final coverage report;
- automatic inventory test that fails when a new CLI route is not added to the lab.

## Complex scenarios

### 1. Repair lifecycle

Creates before and after packages for a duplicate-charge incident, inherits the human assertion, runs environment-prefixed reproduction and regression commands, compares reports, verifies linked passing evidence, generates an AI handoff, records AI/history data, builds the workbench, and exports the package.

### 2. Multi-bug service

Runs the existing six-defect shop-service example and confirms that known database failures remain visible as non-zero command results, verification blockers, and a `needs_repair` handoff.

### 3. Security and integrity incident

Confirms that raw credentials and personal data are blocked by privacy, redaction, and export gates. A sanitized payload passes all gates, then a post-manifest tamper is detected by strict integrity verification.

### 4. Extension governance

Discovers and validates an Adapter and Plugin, records dry runs without execution, then performs explicitly approved local execution. The same run covers Schema validation, conformance, distribution readiness, CI reporting, knowledge indexing, and archive governance.

### 5. Concurrent package writers

Starts two independent `doctor-link record` processes against one after-state package and verifies that both records survive.

### 6. Automatic solve approval gate

Creates a clean Git-backed Python project with a real duplicate-charge defect, runs both configured failing checks through `doctor-link solve`, and proves that the default result is `approval_required`: evidence and a Codex prompt preview are written, but no repair branch or code edit occurs without `--allow-repair`.

### 7. JavaScript automatic solve approval gate

Creates a clean Git-backed Node.js project with a real arithmetic defect and a `node:test` contract. The installed wheel must detect the project as JavaScript, discover `npm test`, reproduce the failure, hash-protect `package.json` and the test file, and stop at `approval_required` without editing code.

## Run

Install development dependencies and build distribution artifacts first:

```bash
python -m pip install -e '.[dev]'
python -m build
python examples/full-capability-lab/run-all.py --dist dist
```

To validate an installed wheel explicitly:

```bash
python examples/full-capability-lab/run-all.py \
  --doctor-link /path/to/clean-venv/bin/doctor-link \
  --dist dist \
  --out /tmp/doctor-link-full-capability
```

The same `--out` path can be run again safely. The lab marks directories it
creates and resets only those marked directories before a rerun. It refuses to
replace a non-empty directory without its valid lab marker, so an accidental
path cannot overwrite unrelated data.

## Output

The output directory contains:

- `full-capability-validation.json`: exact route coverage, exit codes, arguments, scenario checks, and log paths;
- `full-capability-validation.md`: human-readable result;
- `command-logs/`: stdout and stderr for every command invocation;
- diagnostic packages, handoff, workbench, archive, knowledge, integrity, privacy, conformance, CI, and distribution artifacts.

A successful run means all 68 declared routes execute through 77 real command invocations and all 14 scenario-level invariants pass. The automatic-solve, guided-assistant, and benchmark scenarios deliberately stop at the approval gate, so the lab does not call Codex, upload data, publish a release, or call a hosted service. Node.js and npm are required for the JavaScript scenario.
