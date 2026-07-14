# pipx Installation Validation

Status date: 2026-07-14

Doctor link v0.5.0 was installed into a clean, temporary pipx home directly from the immutable GitHub Release wheel:

```bash
pipx install https://github.com/linkyang01/doctor-link/releases/download/v0.5.0/doctor_link-0.5.0-py3-none-any.whl
```

Observed result:

- pipx installed package `doctor-link 0.5.0` with Python 3.12.13;
- the `doctor-link` application entrypoint was created;
- `doctor-link --version` returned `doctor-link, version 0.5.0`;
- `doctor-link preflight . --json` returned `passed` with zero blockers and zero warnings.

This proves the isolated application installation path before registry publication. A final `pipx install doctor-link==0.5.0` check remains required after PyPI Trusted Publishing succeeds.

