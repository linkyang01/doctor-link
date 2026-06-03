# P7.7 Plugin SDK Runtime

Status: runtime implementation with post-P7 hardening

## Scope

P7.7 turns the Plugin SDK planning specification into a local-first runtime layer.

The implementation supports discovering plugin manifests, validating plugin metadata, validating permissions, validating extension points, and creating local plugin run records under an explicit local process boundary.

Post-P7 hardening changes plugin execution semantics: `doctor-link plugin run` is a dry-run by default and does not execute the configured local command unless `--allow-run` is passed.

## Implemented runtime changes

### Plugin manifest

Plugins are declared with `plugin.yml` or `plugin.yaml` files under one of the default locations:

```text
.doctorlink/plugins/
plugins/
DoctorPlugins/
```

A minimal manifest:

```yaml
schema: doctor-link-plugin-v1
id: demo-plugin
name: Demo Plugin
version: 0.1.0
extension_points:
  - verification
permissions:
  - run_local_command
commands:
  verification:
    - python
    - -c
    - print('verification-ok')
```

### Supported extension points

P7.7 supports four runtime extension point names:

- `collector`;
- `renderer`;
- `handoff`;
- `verification`.

### Supported permissions

P7.7 supports these local permission names:

- `read_project`;
- `write_reports`;
- `run_local_command`.

### Plugin discovery

Command:

```bash
doctor-link plugin list .
```

JSON output:

```bash
doctor-link plugin list . --json
```

The command scans the default plugin roots or a supplied override:

```bash
doctor-link plugin list . --plugins-dir .doctorlink/plugins --json
```

### Plugin validation

Command:

```bash
doctor-link plugin validate .doctorlink/plugins/demo-plugin/plugin.yml
```

Validation checks:

- supported schema;
- plugin id;
- plugin name;
- plugin version;
- supported extension points;
- supported permissions;
- `run_local_command` command requirements;
- command presence for declared extension points.

Blocking findings make the plugin invalid. Missing commands for declared extension points are warnings unless the permission model makes commands mandatory.

### Local plugin dry-run

Command:

```bash
doctor-link plugin run demo-plugin verification . --json
```

By default, the run command:

- discovers the plugin;
- validates the manifest;
- verifies the requested extension point;
- enforces `run_local_command` permission;
- records the configured command;
- does not execute the configured command;
- writes a local run record with `status: dry-run`;
- appends an audit record with `dry_run: true` and `explicit_user_approval: false`.

Generated files are written to:

```text
DoctorReports/plugins/
```

Example outputs:

```text
demo-plugin-verification-run.json
plugin-audit.jsonl
```

### Explicit local plugin execution

To actually execute the configured local command, pass explicit approval:

```bash
doctor-link plugin run demo-plugin verification . --allow-run --json
```

With `--allow-run`, Doctor link:

- runs the configured local command from the project root;
- captures stdout, stderr, return code, timestamps, and command arguments;
- writes a local run record;
- appends an audit record with `dry_run: false` and `explicit_user_approval: true`.

### Local process boundary

P7.7 provides an explicit local process boundary. It does not install remote code, download plugins, grant credentials, or provide hard OS sandboxing. Plugin commands are local commands configured by the user.

The audit record includes:

- plugin id;
- plugin name;
- plugin version;
- extension point;
- permissions;
- command;
- status;
- timestamps;
- return code;
- dry-run flag;
- explicit user approval flag;
- local execution boundary flag;
- sandbox boundary label.

## CLI examples

List plugins:

```bash
doctor-link plugin list . --json
```

Validate a manifest:

```bash
doctor-link plugin validate .doctorlink/plugins/demo-plugin/plugin.yml --json
```

Create a dry-run record:

```bash
doctor-link plugin run demo-plugin verification . --json
```

Execute with explicit approval:

```bash
doctor-link plugin run demo-plugin verification . --allow-run --json
```

Run with explicit output directory:

```bash
doctor-link plugin run demo-plugin collector . --allow-run --out DoctorReports/plugins --json
```

## Safety boundaries

P7.7 does not:

- install third-party code;
- download remote plugins;
- grant extra permissions beyond manifest validation;
- manage secrets;
- provide hard OS-level sandbox isolation;
- claim network isolation for child processes;
- implement a hosted plugin marketplace.

Plugin commands are local commands configured by the user. Users should review plugin manifests before running them with `--allow-run`.

## Validation

P7.7 includes tests for:

- plugin manifest loading;
- schema validation;
- permission validation;
- extension point validation;
- plugin discovery;
- plugin dry-run records;
- explicit plugin execution with `--allow-run`;
- plugin audit records;
- `doctor-link plugin list`;
- `doctor-link plugin validate`;
- `doctor-link plugin run`.
