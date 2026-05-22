# Collector Extension Points

Doctor link collectors gather local evidence and write it into diagnostic packages.

P5 documents supported extension patterns without adding a plugin runtime.

## Existing collector inputs

Current collection paths include:

- environment summaries;
- log files;
- command outputs;
- media probes;
- attachments;
- reproduction outputs;
- test matrix outputs.

## Configuration-first extension

Projects can extend collection behavior through `.doctorlink/collect.yml` and CLI options.

Example:

```yaml
project_root: .
logs:
  - logs/*.log
commands:
  - python --version
  - pytest -q
attachments:
  - screenshots/example.png
redact: true
redact_email: true
redact_phone: true
```

## Output contract

Collector outputs should be recorded as evidence with:

- stable evidence ID;
- evidence kind;
- source command or file;
- package-relative path;
- concise human-readable title or content summary.

## Privacy rule

Collector extensions should collect the smallest necessary evidence and preserve redaction options.

## Future SDK boundary

A future SDK may expose a stable collector API, but P5 does not promise runtime plugin loading or third-party package discovery.
