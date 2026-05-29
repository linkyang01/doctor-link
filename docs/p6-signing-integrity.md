# P6.6 Diagnostic Package Signing and Integrity

Status: planning specification only

## Scope

P6.6 defines the signing and integrity model for future Doctor link diagnostic packages.

This phase does not implement real cryptographic signing, key management, hosted verification, cloud services, external accounts, release publishing, or PyPI publishing.

## Goals

The goals are to define:

- package content hashing model;
- manifest integrity fields;
- package signature metadata;
- signing key policy;
- verification command plan;
- tamper detection behavior;
- signed package export checklist;
- security review requirements.

## Package content hashing model

A future signed package should calculate hashes for selected package files.

Recommended default hash algorithm:

```text
sha256
```

Recommended hash scope:

```text
doctor-report.json
ai-context.json
user-assertions.json
verification-result.json
schema-validation-result.json
handoff-manifest.json
```

Optional hash scope:

```text
attachments/
logs/
.doctorlink-web/
```

Rules:

- Hashes should be calculated over file bytes.
- Path names should be normalized to package-relative POSIX paths.
- Generated timestamp fields should not be silently excluded unless documented.
- Missing optional files should be recorded as missing, not ignored silently.

## Manifest integrity fields

A future integrity manifest should include:

```text
schema_version
package_id
created_at
hash_algorithm
hash_scope
files
missing_files
signature
verification
```

Each file entry should include:

```text
path
size_bytes
sha256
required
```

## Package signature metadata

A future signature block should include:

```text
signature_id
signature_algorithm
signed_at
signer
key_id
signature_value
signed_manifest_hash
```

If a package is unsigned, the signature block should explicitly state:

```text
status: unsigned
```

## Signing key policy

Signing keys should follow these rules:

- Never store private keys in diagnostic packages.
- Never commit private keys to the repository.
- Support local signing first.
- Record only public key metadata in exported packages.
- Require explicit user authorization before signing.
- Keep test keys clearly marked as test-only.

## Verification command plan

A future verification command may be:

```bash
doctor-link integrity verify <package_dir>
```

Possible options:

```bash
--manifest integrity-manifest.json
--json
--strict
```

The command should verify:

- required files exist;
- file hashes match the integrity manifest;
- package-relative paths are safe;
- signature metadata is structurally valid;
- signed manifest hash matches when a signature is present.

## Tamper detection behavior

Tamper detection should report:

```text
missing_required_file
hash_mismatch
unexpected_file
unsafe_path
invalid_signature_metadata
unsupported_algorithm
unsigned_package
```

Rules:

- Hash mismatches are errors.
- Missing required files are errors.
- Missing optional files are warnings.
- Unsigned packages are warnings unless strict mode requires signatures.
- Unsupported algorithms are errors.

## Signed package export checklist

Before exporting a signed package:

- schema validation should pass;
- conformance validation should pass when fixtures apply;
- redaction report should be reviewed;
- user assertions should be preserved;
- verification result should be present when available;
- integrity manifest should be generated;
- signature metadata should be present or explicitly marked unsigned;
- exported archive should not include private keys.

## Security review requirements

Before implementing real signing, review:

- supported algorithms;
- key storage policy;
- path traversal handling;
- canonicalization rules;
- private key protection;
- test key isolation;
- error reporting behavior;
- strict mode behavior;
- compatibility with historical packages.

## Non-goals

P6.6 does not include:

- real signing implementation;
- private key management;
- hosted verification service;
- release signing;
- cloud key storage;
- account system;
- marketplace trust badges;
- public release publishing;
- PyPI publishing.
