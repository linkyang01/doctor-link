# Sensitive Data Handling

Doctor link diagnostic packages may contain sensitive data if users collect logs, command outputs, attachments, screenshots, or AI handoff packages.

## Common sensitive data

Potentially sensitive content includes:

- API keys and tokens;
- passwords;
- email addresses;
- phone numbers;
- private repository paths;
- customer data;
- screenshots containing private UI;
- logs containing identifiers or URLs;
- AI prompts containing confidential business context.

## Collection guidance

Prefer narrow collection commands:

```bash
doctor-link collect <package_dir> --logs "logs/app.log" --redact-email --redact-phone
```

Use custom redaction patterns when project-specific secrets are known:

```bash
doctor-link collect <package_dir> --command "env" --redact-pattern "TOKEN_[A-Z0-9]+"
```

## Review guidance

Before sharing:

- open `evidence-list.md`;
- inspect `evidence/` subdirectories;
- inspect `ai-task.md`;
- inspect generated handoff packages;
- inspect zip exports before sending.

## Redaction limitations

Redaction is best-effort. It cannot guarantee removal of every secret or private value.

Do not rely on redaction alone for highly sensitive production data.

## Safe sharing pattern

1. Collect only necessary evidence.
2. Redact during collection.
3. Review generated files.
4. Remove unnecessary attachments.
5. Share the smallest diagnostic package that still proves the issue.
