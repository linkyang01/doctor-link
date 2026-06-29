# Python API Bug Example

A minimal Python service with a reproducible API bug for Doctor link walkthroughs.

## Scenario

`GET /health` works, but `GET /users` returns HTTP 500 because the handler reads a missing config key.

## Layout

```text
examples/python-api-bug/
├── README.md
├── src/api.py
├── config/app.yml
├── logs/api.log
├── tests/test_api.py
└── .doctorlink/
    ├── diagnosis.yml
    ├── reproduce.yml
    └── test-matrix.yml
```

## Walkthrough

From the repository root:

```bash
doctor-link diagnose-now examples/python-api-bug --full --summary "GET /users returns 500"
doctor-link reproduce run api-500 examples/python-api-bug
doctor-link test run examples/python-api-bug --job unit-api
```

Open the generated HTML report from the `diagnose-now --full` output, then generate AI handoff:

```bash
PACKAGE_DIR="<path-from-diagnose-now-output>"
doctor-link handoff "$PACKAGE_DIR" --tool cursor
```

Give the handoff folder to your AI coding tool with the user assertion:

```bash
doctor-link assert "$PACKAGE_DIR" \
  --statement "GET /users returns HTTP 500" \
  --expected "HTTP 200 with user list" \
  --actual "HTTP 500 Internal Server Error"
```