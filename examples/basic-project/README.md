# Basic Doctor link Example Project

This example shows a minimal project layout for Doctor link.

## Files

```text
examples/basic-project/
├── README.md
├── sample_app.py
└── .doctorlink/
    ├── diagnosis.yml
    ├── reproduce.yml
    └── test-matrix.yml
```

## Try it

From the repository root:

```bash
doctor-link strategy validate examples/basic-project --json
doctor-link reproduce list examples/basic-project --json
doctor-link test list examples/basic-project --json
```

Run the example test matrix:

```bash
doctor-link test run examples/basic-project --json
```

This example is local-only and does not publish or upload anything.
