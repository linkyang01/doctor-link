# Doctor link

Doctor link is a human-AI shared diagnostic layer for software projects.

Doctor link 是一个面向软件项目的人机协同诊断层。

## Read the full README

- [English](docs/readme/README.en.md)
- [中文](docs/readme/README.zh-CN.md)

## Install from source

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
python -m pip install -e .
doctor-link --version
```

## CLI docs

- [diagnose-now](docs/diagnose-now.md) - quick local diagnosis, summary output, `--output`, `--json`, and `--report-json`
- `doctor-link preflight . --json` - inspect configuration, tools, and repository commands without executing them
- [No-code quick start (EN)](docs/guides/no-code-quick-start.en.md) | [非程序员入门 (ZH)](docs/guides/no-code-quick-start.zh-CN.md)

## Current status

The current source version is `0.1.2`. Local repair validation passed on 2026-07-13, including the full test suite, E2E, self-validation, P7 runtime validation, security scanning, package build, and installed-wheel smoke tests. `v0.1.2` has not been published yet; release and cloud-CI status must only be updated after GitHub verifies the pushed commit.

当前源码版本为 `0.1.2`。2026-07-13 已完成本地修复验证，包括全量测试、E2E、自验证、P7 runtime、安全扫描、构建和已安装 wheel 冒烟测试。`v0.1.2` 尚未发布；只有修复提交推送并通过 GitHub 校验后，才能更新云端认证和正式发布状态。

## Main project areas

- `doctor_link/` - Python package source
- `tests/` - automated tests
- `scripts/` - validation and helper scripts
- `docs/` - documentation, audits, roadmap, and archived TODOs
- `examples/` - examples and templates
- `.github/` - GitHub Actions workflows
