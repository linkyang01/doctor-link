# Public-project validation

This validation checks Doctor link against six pinned public repositories: three Python and three JavaScript projects. It does not install or execute project dependencies and does not modify the cloned repositories. The runner verifies the exact commit, invokes Doctor link's read-only preflight, and records structured results.

```bash
python scripts/validate_public_projects.py \
  --manifest examples/public-project-validation/projects.json \
  --out /tmp/doctor-link-public-project-validation
```

Passing means every repository was cloned at its declared immutable commit and Doctor link returned a successful preflight report with no blockers. This complements the 24-scenario fault corpus and the offline [failure-mode harness](../failure-mode-validation/README.md). The pin set intentionally includes Node.js projects (`p-limit`, `chalk`, `axios`) as public demo targets for external users. It does not claim that every upstream project's full test suite was executed.
