# P7.7 Plugin SDK Runtime

Status: runtime implementation

## Scope

P7.7 turns the Plugin SDK planning specification into a local-first runtime layer.

The implementation supports discovering plugin manifests, validating plugin metadata, enforcing a basic permission model, and running configured local plugin commands under an explicit local process boundary.

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
  - collector
  - renderer
  - handoff
  - verification
permissions:
  - read_project
  - write_reports
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

### Permission model

Supported permissions:

- `read_project`;
- `write_reports`;
- `run_local_command`.

`doctor-link plugin run` requires the plugin manifest to include `run_local_command`. Unsupported permissions are blocking validation findings.

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

### Local plugin execution

Command:

```bash
doctor-link plugin run demo-plugin verification .
```

The run command:

- discovers the plugin;
- validates the manifest;
- verifies the requested extension point;
- enforces `run_local_command` permission;
- runs the configured local command from the project root;
- captures stdout, stderr, return code, timestamps, and command arguments;
- writes a local run record;
- appends an audit record.

Generated files are written to:

```text
DoctorReports/plugins/
```

Example outputs:

```text
demo-plugin-verification-run.json
plugin-audit.jsonl
```

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

Run a plugin extension point:

```bash
doctor-link plugin run demo-plugin verification . --json
```

Run with explicit output directory:

```bash
doctor-link plugin run demo-plugin collector . --out DoctorReports/plugins --json
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

Users should review plugin manifests before running them.

## Validation

P7.7 includes tests for:

- plugin manifest loading;
- plugin permission model enforcement;
- plugin discovery;
- collector, renderer, handoff, and verification extension point declarations;
- local plugin execution;
- plugin audit records;
- `doctor-link plugin list`;
- `doctor-link plugin validate`;
- `doctor-link plugin run`.
