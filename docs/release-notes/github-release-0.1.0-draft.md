# Draft GitHub Release Body: v0.1.0

> Draft only. Do not create this GitHub Release without explicit authorization.

## Doctor link 0.1.0

Doctor link is a local-first diagnostic context layer for AI Coding workflows.

### Included

- Standard diagnostic packages under `DoctorReports/`.
- Evidence collection and verification commands.
- Local read-only diagnostic workbench.
- AI Coding handoff and result intake.
- Assertion compliance and repair risk review.
- Automated before / after diagnosis pipeline.
- Project health summary.
- Productization documentation, examples, privacy review, and release readiness checklist.

### Install from source

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
python -m pip install -e .
```

### Verify

```bash
doctor-link --help
pytest -q
```

### Publishing boundary

This release body is prepared for review only. Do not tag, publish, upload assets, create a GitHub Release, or publish to PyPI without explicit authorization.
