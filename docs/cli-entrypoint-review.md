# CLI Entrypoint Review

Doctor link currently exposes the console script:

```text
doctor-link = doctor_link.p4_cli:main
```

## Current design

- `doctor_link/cli.py` contains the original CLI command group and core commands.
- `doctor_link/p4_cli.py` imports `main` from `doctor_link/cli.py` and registers later P4/P5 commands on the same Click group.
- The installed command points to `doctor_link.p4_cli:main` so both original and later commands are available.

## Review conclusion

The current entrypoint is usable and validated by CI smoke tests, E2E validation, and installed wheel smoke tests.

A larger refactor can later merge command registration into a dedicated package, but P5.9 does not need that change before internal pre-release validation.

## Risk

The main risk is maintainability: contributors may not immediately know that new commands should be registered through the wrapper entrypoint unless this document is read.

## Recommendation

Keep the current entrypoint for v0.1.0 internal validation. Revisit a cleaner command registry in a future maintenance PR.
