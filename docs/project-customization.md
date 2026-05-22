# Project Customization

Doctor link projects can be customized through `.doctorlink/` configuration files.

## Configuration files

Common files:

```text
.doctorlink/
├── doctorlink.yml
├── diagnosis.yml
├── reproduce.yml
├── collect.yml
├── package.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

## Diagnosis strategy

Use `.doctorlink/diagnosis.yml` to define project type, default commands, evidence rules, verification rules, and excluded paths.

## Reproduction entries

Use `.doctorlink/reproduce.yml` to define manual, command, or test reproduction entries.

## Test matrix

Use `.doctorlink/test-matrix.yml` to define executable jobs and informational test cases.

## Evidence collection

Use `.doctorlink/collect.yml` for project-specific logs, commands, probes, and attachments.

## Verification

Use `.doctorlink/verification.yml` to configure write-back behavior and verification expectations.

## Precedence

CLI arguments should override configuration file defaults when both are provided.

## Boundary

Project customization should remain local-first and should not introduce external services or account systems by default.
