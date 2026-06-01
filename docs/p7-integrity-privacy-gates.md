# P7.8 Integrity and Privacy Runtime Gates

Status: runtime implementation

## Scope

P7.8 implements local-first integrity and privacy runtime gates.

The implementation provides file integrity manifests, verification checks, privacy scanning, redaction gates, and export safety gates. It intentionally avoids real signing, key management, remote verification services, or hosted policy systems.

## Implemented runtime changes

### Integrity manifest generator

Command:

```bash
doctor-link integrity manifest . --out DoctorReports/integrity-manifest.json --json
```

The manifest records:

- schema;
- root path;
- generated timestamp;
- unsigned manifest flag;
- file paths;
- SHA-256 hashes;
- file sizes;
- unsigned manifest warning.

The manifest is unsigned by design in P7.8. Real signing or key management remains out of scope unless explicitly authorized later.

### Integrity verify command

Command:

```bash
doctor-link integrity verify . DoctorReports/integrity-manifest.json --json
```

Verification detects:

- unsupported schema;
- unsigned manifest warning;
- hash mismatch;
- missing files;
- unsafe paths;
- manifest paths that escape the root.

Blocking findings return a non-zero CLI exit.

### Privacy policy loader

Default privacy patterns include:

- email address pattern;
- API key / token / secret assignment pattern;
- private key block pattern.

Optional policy file:

```yaml
schema: doctor-link-privacy-policy-v1
allow_export_with_findings: false
exclude_globs:
  - .git/**
  - dist/**
patterns:
  custom_secret: CUSTOM-SECRET-[0-9]+
```

### Privacy scan command

Command:

```bash
doctor-link privacy scan . --policy .doctorlink/privacy.yml --json
```

The scan reads UTF-8 text files, skips binary / undecodable files, applies configured regex patterns, and reports line-level findings.

### Redaction gate command

Command:

```bash
doctor-link privacy redaction-gate . --json
```

The redaction gate blocks when privacy findings remain in the scanned files.

### Export safety gate command

Command:

```bash
doctor-link privacy export-gate . --manifest DoctorReports/integrity-manifest.json --json
```

The export gate combines privacy findings and optional integrity verification findings. It blocks unsafe exports unless the privacy policy explicitly allows export with findings.

## CLI examples

Generate an integrity manifest:

```bash
doctor-link integrity manifest . --out DoctorReports/integrity-manifest.json
```

Verify integrity:

```bash
doctor-link integrity verify . DoctorReports/integrity-manifest.json --out DoctorReports/integrity-verify.json
```

Run privacy scan:

```bash
doctor-link privacy scan . --out DoctorReports/privacy-scan.json
```

Run redaction gate:

```bash
doctor-link privacy redaction-gate . --out DoctorReports/redaction-gate.json
```

Run export safety gate:

```bash
doctor-link privacy export-gate . --manifest DoctorReports/integrity-manifest.json --out DoctorReports/export-gate.json
```

## Safety boundaries

P7.8 does not:

- create cryptographic signatures;
- manage signing keys;
- upload manifests;
- call remote verification services;
- guarantee hard data-loss prevention;
- replace human review before external sharing.

It is a local preflight gate and audit evidence generator.

## Validation

P7.8 includes tests for:

- integrity manifest generation;
- integrity verification;
- hash mismatch detection;
- missing file detection;
- unsafe path detection;
- unsigned manifest warning;
- privacy policy loading;
- default privacy scanning;
- custom privacy pattern scanning;
- redaction gate blocking;
- export gate blocking;
- integrity and privacy CLI commands.
