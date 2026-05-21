# Troubleshooting Guide

## `doctor-link` command not found

Reinstall from source:

```bash
python -m pip install -e .
```

Then check:

```bash
doctor-link --help
```

## `strategy validate` fails

Check that `.doctorlink/diagnosis.yml` exists and is valid YAML.

```bash
doctor-link strategy validate . --json
```

## No reproduction entries found

Create `.doctorlink/reproduce.yml` with a `reproductions` list.

## No test matrix jobs found

Create `.doctorlink/test-matrix.yml` with executable `jobs`.

Legacy `cases` are informational and do not run commands.

## Verification does not show success

Doctor link requires verification evidence. If evidence is missing, pipeline success remains false.

Run:

```bash
doctor-link verify <package_dir> --write-back
doctor-link diagnose verify <after_package> --json
```

## Web view exists but looks stale

Rebuild the static view:

```bash
doctor-link view <package_dir> --build-only
```

## Diagnostic package contains sensitive data

Use redaction options during collection and review exported packages before sharing.

```bash
doctor-link collect <package_dir> --logs "logs/*.log" --redact-email --redact-phone
```

## Release or publish command needed

Publishing is not part of normal troubleshooting. Do not publish a release, create a GitHub Release, or publish to PyPI without explicit authorization.
