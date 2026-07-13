# Doctor link Full Capability Lab

This lab runs every Doctor link CLI capability through realistic local scenarios. It is an executable validation asset, not a list of help commands.

## Coverage contract

- 62/62 capability routes, including the version entrypoint;
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

## Output

The output directory contains:

- `full-capability-validation.json`: exact route coverage, exit codes, arguments, scenario checks, and log paths;
- `full-capability-validation.md`: human-readable result;
- `command-logs/`: stdout and stderr for every command invocation;
- diagnostic packages, handoff, workbench, archive, knowledge, integrity, privacy, conformance, CI, and distribution artifacts.

A successful run means all 62 declared routes executed through 70 real command invocations and all eight scenario-level invariants passed. It does not upload data, publish a release, or call a hosted service.
