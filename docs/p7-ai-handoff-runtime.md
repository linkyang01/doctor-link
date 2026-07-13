# P7.3 AI Tool Runtime Handoff Implementation

Status: runtime implementation

## Scope

P7.3 upgrades the P3 AI collaboration layer from a generic handoff package into a tool-profile-driven runtime handoff system.

## Implemented runtime changes

### Target tool profiles

Doctor link now has runtime handoff profiles for:

- Codex
- Cursor
- Continue
- Aider
- OpenHands
- Claude Code
- Grok Build
- Windsurf
- Cline
- Generic Markdown/JSON

Each profile defines:

- tool key;
- display name;
- instruction filename;
- tool-specific notes;
- preferred context mode;
- terminal and patch workflow capability metadata;
- maximum recommended files;
- required handoff files;
- optional handoff files;
- allowed and denied file policy.

### Compatibility checker

The handoff runtime now writes:

```text
handoff-compatibility.json
```

The compatibility report includes:

- status;
- missing required files;
- missing optional files;
- included files;
- skipped files;
- missing evidence warnings;
- privacy warnings;
- profile guidance.

Compatibility status values include:

- `ready`
- `ready_for_verification_review`
- `needs_evidence`
- `needs_repair`
- `needs_review`
- `blocked_missing_required_files`

The compatibility report also includes `verification_status`. A failed or unknown test record keeps verification at `not_verified`, which produces `needs_repair`; missing evidence produces `needs_evidence`; and `candidate_verified` produces `ready_for_verification_review`. Historical comparison text cannot override the latest verification result.

### Tool-specific instruction generation

The generated instruction file now includes:

- compatibility status;
- required human-assertion rule;
- tool-specific guidance;
- file inclusion policy;
- included files;
- missing files;
- missing evidence warnings;
- privacy warnings;
- AI task;
- investigation boundary;
- verification checklist;
- evidence list;
- user assertions.

### File inclusion policy enforcement

The handoff builder now enforces a conservative local file policy:

- Markdown, JSON, log, text, CSV and YAML evidence can be copied.
- Archives, media and binary-looking handoff targets are skipped.
- Evidence referenced in `doctor-report.json` is considered for inclusion, subject to policy and profile limits.
- Profile `max_recommended_files` limits the candidate set.

### Missing evidence warnings

The handoff runtime inspects `verification-result.json` and surfaces:

- current verification status;
- missing evidence;
- tests or verification actions to rerun;
- failed, partial, or unknown blocking test records;
- missing evidence list file.

### Privacy warnings

The handoff runtime scans small candidate text files for sensitive patterns:

- possible API keys, tokens, secrets or passwords;
- private key blocks;
- email addresses.

These warnings do not redact content. They instruct the user or AI operator to review before external sharing.

### Enhanced AI result ingestion

AI repair result records now include:

- `repair_session_id`;
- `tool`;
- timestamp;
- verification-required notice.

The old `ai-repair-result.json` and `ai-repair-result.md` outputs remain compatible.

### Repair session management

Doctor link now writes:

```text
ai-repair-sessions.json
ai-repair-sessions.md
```

A repair session tracks:

- repair session id;
- tool;
- created and updated timestamps;
- AI result ids;
- history round ids;
- open verification-required status.

`diagnosis-history` rounds can be attached to an existing repair session, enabling multi-round repair workflows.

## CLI changes

### Handoff

```bash
doctor-link handoff list
doctor-link handoff check <package_dir> --tool grok --json
doctor-link handoff <package_dir> --tool claude-code
doctor-link handoff <package_dir> --tool claude-code --json
```

`handoff list` shows supported profiles. `handoff check` runs compatibility pre-check without copying files. Generate still accepts the shorthand `handoff <package_dir>` and prints the compatibility report path in addition to manifest and instruction paths.

### AI result

```bash
doctor-link ai-result <package_dir> \
  --summary "patched parser" \
  --repair-session-id repair_session_001 \
  --tool codex
```

### Diagnosis history

```bash
doctor-link diagnosis-history <package_dir> \
  --ai-pass "second pass" \
  --repair-session-id repair_session_001 \
  --tool codex
```

## Safety boundaries

P7.3 does not:

- call external AI tools;
- connect to cloud services;
- upload package contents;
- publish packages;
- create releases or tags;
- bypass privacy warnings;
- mark repairs verified without verification evidence.

## Validation

P7.3 includes tests for:

- all target tool profiles;
- Claude Code handoff package generation;
- compatibility report generation;
- tool-specific instruction content;
- file inclusion policy enforcement;
- missing evidence warnings;
- privacy warnings;
- repair session id support;
- multi-round repair session tracking;
- CLI support for `--tool` and `--repair-session-id`.
