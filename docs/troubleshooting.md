# Troubleshooting Guide

## Package export is blocked by the privacy gate

Run `doctor-link privacy scan <package_dir> --json`, redact the reported files, and run `doctor-package` again. If an authorized reviewer deliberately accepts the remaining risk, `--allow-unsafe-export` permits the archive and records the override in its manifest.

## A legacy export still uses manifest.json

Run `doctor-link schema migrate <package_dir> --json`. The migration recognizes only export-shaped legacy payloads, creates the new portable `package-export-manifest.json`, and preserves backups. Formal package manifests are not modified.

## Export is interrupted or disk space is insufficient

Doctor link builds the zip beside the destination and replaces the destination only after the new archive closes successfully. Free destination space and rerun the same command; a previous complete archive remains unchanged after interruption or capacity failure.

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
