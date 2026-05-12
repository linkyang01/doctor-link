# Doctor link Commands

## Current commands

### init

Create a diagnostic workspace.

```bash
doctor-link init DoctorWorkspace
```

### scan

Scan a test library and print detected files.

```bash
doctor-link scan ./VlyTestLibrary
```

### plan

Generate a test plan from detected files.

```bash
doctor-link plan ./VlyTestLibrary
```

### report

Generate Markdown and JSON reports.

```bash
doctor-link report ./VlyTestLibrary --out DoctorReports
```

### ai-task

Generate an AI-ready debugging task draft.

```bash
doctor-link ai-task ./VlyTestLibrary --out DoctorReports
```

## Planned commands

```bash
doctor-link probe ./VlyTestLibrary
doctor-link record ./VlyTestLibrary
doctor-link doctor ./DoctorReports/latest
doctor-link github issue ./DoctorReports/latest
```
