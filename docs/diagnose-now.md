# diagnose-now

Run a quick diagnosis for a local media library and write a summary file.

## Default usage

```bash
doctor-link diagnose-now /path/to/library
```

This writes:

```text
/path/to/library/.doctor-link/summary.md
```

The summary includes:

- file count
- extension counts
- basic recommendations

## Custom output directory

```bash
doctor-link diagnose-now /path/to/library --output /path/to/report
```

This writes:

```text
/path/to/report/summary.md
```

The output directory is excluded from the scan so repeated runs do not change the file count.

## JSON output

```bash
doctor-link diagnose-now /path/to/library --json
```

Example output:

```json
{"summary": "/path/to/library/.doctor-link/summary.md"}
```

You can combine JSON output with a custom output directory:

```bash
doctor-link diagnose-now /path/to/library --output /path/to/report --json
```
