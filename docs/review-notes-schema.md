# Review Notes Schema Draft

Review notes are a deferred write-back capability.

P2+ keeps the local Web UI read-only by default. This schema defines the future data shape only. It does not enable automatic Web UI write-back.

## Proposed file

`review-notes.json`

## Proposed structure

```json
{
  "version": 1,
  "notes": [
    {
      "note_id": "note_001",
      "created_at": "2026-01-01T00:00:00Z",
      "reviewer": "local-user",
      "source_section": "verification",
      "related_evidence_ids": ["ev_001"],
      "related_assertion_ids": ["assertion_001"],
      "content": "Review note text",
      "status": "open"
    }
  ]
}
```

## Boundary

A future implementation must remain explicit and auditable:

- no default write-back;
- no hidden mutation of diagnostic packages;
- reviewer, time, source section, and content must be recorded;
- any Web UI write-back requires a separate ADR before implementation.
