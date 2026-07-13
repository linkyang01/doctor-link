# Automated Diagnosis Reliability

This guide defines how Doctor link executes configured checks, records their evidence, decides verification status, and prepares AI handoff packages. The rules are intentionally conservative: a failure stays visible until a linked passing result replaces it.

## Safe configured commands

Reproduction and test-matrix commands run as argument vectors without invoking a shell. A configuration may use normal quoting, sequential `&&`, and leading environment assignments:

```yaml
command: PYTHONPATH=src MODE=regression python -m pytest tests/test_checkout.py
```

Environment assignments must appear before the executable. Values may reference variables inherited from the Doctor link process. Pipelines, redirection, background execution, semicolons, command substitution, and other shell control operators are rejected.

Commands run from the configured project root and share one total timeout budget across `&&` segments. Execution stops on the first failing or timed-out segment.

## Exit-code contract

JSON output and process status describe the same outcome:

| Command | Success | Failure signal |
| --- | --- | --- |
| `doctor-link reproduce run` | result is `passed` or `manual` | exits non-zero for failed, timed-out, missing, or invalid reproduction |
| `doctor-link test run` | every required job passed | exits non-zero when any required job fails; optional failures remain in JSON without failing the command |
| `doctor-link verify` | status is `candidate_verified`, `ready`, or `verified` | exits non-zero for missing or blocking verification states |
| `doctor-link diagnose verify` | the combined diagnosis pipeline reports success | exits non-zero while comparison or verification remains blocked |

The command emits its JSON before exiting, allowing CI and scripts to inspect details even on an expected failure.

## Automated evidence write-back

Pass `--package-dir` to attach an automated result to a diagnostic package:

```bash
doctor-link reproduce run repro-login . --package-dir "$PACKAGE_DIR" --json
doctor-link test run . --package-dir "$PACKAGE_DIR" --json
```

Each result updates:

- its JSON file under `evidence/reproductions/` or `evidence/test-results/`;
- the evidence, timeline, and test-record collections in `doctor-report.json`;
- marked blocks in `evidence-list.md` and `timeline.md`;
- related assertion IDs in the evidence and AI task context.

Reproduction and test job IDs are stable. Rerunning the same item replaces the earlier result and marked Markdown blocks, so a current pass cannot coexist with a stale failure for the same configured check.

## Linking human assertions

Configurations can link checks directly by ID or by statement:

```yaml
reproductions:
  - id: repro-login
    title: Login timeout
    kind: command
    command: PYTHONPATH=src python -m pytest tests/test_auth.py
    related_assertion_ids:
      - assert_known_id
    related_assertion_statements:
      - "P1: login timeout in auth.log"
```

Statement matching is case-insensitive and whitespace-normalized. Statement links are resolved to the package's current assertion IDs when the check is recorded, which avoids hard-coding dynamically generated IDs in repository configuration.

An after-state package inherits the before package's human assertions and investigation boundary. An inherited assertion is resolved only when an after-state test record:

1. links to that assertion ID; and
2. has status `passed`.

Deleting an assertion, omitting it from the after report, increasing the number of test records, or adding unrelated passing evidence is not proof of resolution. Linked records with `failed`, `partial`, or `unknown` status remain blockers.

## Comparison and verification status

Before/after comparison uses these conservative states:

- `not_verified`: an original assertion lacks linked passing evidence, a new assertion exists, or an after-state test is not passing;
- `candidate_verified`: every original assertion has linked passing after-state evidence and no blocking test exists; human review is still required;
- `needs_review`: available evidence is insufficient to make either classification.

Verification includes every failed, partial, or unknown test record in `blocking_test_records` and `tests_to_rerun`. Repeated comparison and verification runs replace their generated evidence and Markdown sections. When blockers are later resolved, obsolete generated commands and blocker requests are removed from the AI task.

## AI handoff status

Handoff compatibility exposes both its own status and the source `verification_status`:

| Verification condition | Handoff status |
| --- | --- |
| required handoff file missing | `blocked_missing_required_files` |
| privacy warning found | `needs_review` |
| verification is `not_verified` | `needs_repair` |
| verification is `missing_evidence`, or evidence warnings remain | `needs_evidence` |
| verification is `candidate_verified` | `ready_for_verification_review` |
| no blockers remain | `ready` |

Generated instructions state that the latest verification result takes precedence over historical evidence. Failed tests and required reruns are included in the warnings given to the target AI tool.

## Concurrent package updates

Doctor link serializes package mutations across processes with a package-local lock and writes JSON/Markdown through atomic replacement. Concurrent `record`, assertion, reproduction, test-matrix, comparison, and verification operations therefore do not silently overwrite each other. Abandoned locks older than the recovery threshold are removed automatically.

## End-to-end complex example

Run the six-defect example from the repository root:

```bash
bash examples/shop-service-multi-bug/run-example.sh
```

The example validates that five reproductions pass as expected, the database reproduction fails as expected, one required matrix job fails, four assertions receive linked evidence, verification remains `not_verified`, and handoff remains `needs_repair`. A zero exit from the script means Doctor link represented the unresolved defects correctly; it does not mean the example application was repaired.

## Privacy and integrity boundary

Evidence remains local unless the user exports or shares it. Before external handoff, run the privacy/redaction and integrity gates documented in [Sensitive Data Handling](sensitive-data-handling.md) and [Export Security Checklist](export-security-checklist.md). Concurrency and status changes do not bypass those gates.
