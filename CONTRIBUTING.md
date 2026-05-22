# Contributing to Doctor link

Thank you for improving Doctor link.

## Principles

- Evidence first.
- Reproduction first.
- Human-confirmed issues first.
- Verification before closure.
- Local-first and privacy-aware.

## Development setup

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
pytest -q
```

## Pull request expectations

A PR should include:

- a clear description;
- related issue or TODO reference;
- tests or documentation updates;
- no secrets or private data;
- no release publishing unless explicitly authorized.

## Documentation expectations

User-facing changes should update relevant docs under `docs/` and README files when appropriate.

## Release boundary

Do not create GitHub Releases, tags intended for public distribution, or PyPI uploads without explicit authorization.
