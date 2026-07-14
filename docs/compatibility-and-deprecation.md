# Compatibility and Deprecation Policy

## Supported runtime

The current release supports Python 3.10 through 3.14 and is continuously checked on Ubuntu, macOS, and Windows. Optional external tools and project-specific commands remain the responsibility of the diagnosed project.

## Compatibility contract

- Patch releases preserve documented CLI behavior and package formats except when a security fix requires a stricter safe default.
- Minor releases may add commands, fields, adapters, and package capabilities while retaining backward-readable data or an explicit migration path.
- Major releases may remove or redesign behavior after documented notice.
- Diagnostic package schemas declare their version. Readers should reject unsupported future schemas rather than silently reinterpret them.

## Deprecation process

A planned removal must be documented in the changelog and migration guidance. Whenever practical, the old path emits a warning for at least one minor release before removal. Security-sensitive behavior may be disabled immediately; the release notes must explain the reason and replacement.

## Support window

The latest release line receives fixes. Older releases remain available as immutable artifacts but are not promised ongoing fixes. Users reporting a defect should confirm it against the latest release when practical.
