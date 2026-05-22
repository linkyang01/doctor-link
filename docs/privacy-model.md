# Privacy Model

Doctor link is local-first and evidence-first.

## Local-first boundary

Doctor link commands operate on local files and local diagnostic packages by default.

Doctor link does not, by default:

- upload diagnostic packages;
- create external accounts;
- call paid cloud services;
- publish releases;
- send user evidence to third-party services.

## Diagnostic package contents

A diagnostic package may include:

- environment summaries;
- command output;
- logs;
- media probe summaries;
- screenshots or attachments when explicitly collected;
- user-confirmed issues;
- AI task context;
- verification results;
- before / after comparison metadata.

Because these files may contain sensitive data, users should review packages before sharing them.

## Human-confirmed issue data

User assertions can contain product names, private workflows, customer descriptions, or confidential issue details.

Treat `user-assertions.json`, `ai-task.md`, and AI handoff packages as potentially sensitive.

## Redaction model

Doctor link provides redaction options for collected text evidence. Redaction helps reduce obvious secrets, emails, phone numbers, and custom patterns, but it is not a guarantee that all sensitive data is removed.

Users remain responsible for reviewing diagnostic packages before external sharing.

## Sharing guidance

Before sharing a package:

1. Run redaction when collecting logs and command outputs.
2. Review `evidence/` files.
3. Review `ai-task.md` and handoff packages.
4. Remove private attachments that are not necessary.
5. Avoid sharing raw customer data unless explicitly approved.
