# Real GitHub capability validation

This suite uses pinned source commits from Click, p-limit, and Chalk. Unlike the public-project preflight set, it runs each project's real tests, applies one reversible production-code mutation without changing tests, asks Doctor link to find and execute a reproduction from ordinary language, checks exact file/line/function localization, and requires a reversible counterfactual experiment to confirm that restoring the candidate makes the failure disappear.

Dependencies are intentionally prepared outside the harness so network installation is explicit and reviewable:

1. clone each repository at the commit in `scenarios.json` under one workspace;
2. for Click, create `.doctorlink-validation-venv` with Python 3.10+ and install the project plus `pytest<9`;
3. for p-limit and Chalk, run `npm install --no-package-lock --no-audit --no-fund`;
4. run:

```bash
python scripts/validate_real_github_capability.py \
  --workspace /path/to/prepared-projects \
  --doctor-link "$(command -v doctor-link)" \
  --out /tmp/doctor-link-real-github-capability
```

The harness restores each mutated file in a `finally` block and requires the final Git status to match its initial status. It never invokes repair or writes to the upstream repository.
