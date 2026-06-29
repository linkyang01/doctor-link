# Doctor link

Doctor link is a human-AI shared diagnostic layer for software projects.

Doctor link 是一个面向软件项目的人机协同诊断层。

## Read the full README

- [English](docs/readme/README.en.md)
- [中文](docs/readme/README.zh-CN.md)

## Install (GitHub Release)

```bash
pip install https://github.com/linkyang01/doctor-link/releases/download/v0.1.2/doctor_link-0.1.2-py3-none-any.whl
doctor-link --version
```

From source: `pip install -e .` after cloning this repository.

## CLI docs

- [diagnose-now](docs/diagnose-now.md) - quick local diagnosis, summary output, `--output`, `--json`, and `--report-json`
- [No-code quick start (EN)](docs/guides/no-code-quick-start.en.md) | [非程序员入门 (ZH)](docs/guides/no-code-quick-start.zh-CN.md)

## Current status

Doctor link has completed P0-P7 local runtime implementation, post-P7 hardening, and public GitHub Releases (`v0.1.2` Latest). The project remains local-first: no hosted platform, account system, or telemetry. PyPI publication is optional and not required for GitHub distribution.

Doctor link 已完成 P0-P7 本地运行能力、Post-P7 加固，并发布 GitHub 正式版（`v0.1.2`，Latest）。项目仍坚持本地优先：无托管平台、账号体系或遥测。PyPI 为可选项，GitHub Release 即可安装使用。

## Main project areas

- `doctor_link/` - Python package source
- `tests/` - automated tests
- `scripts/` - validation and helper scripts
- `docs/` - documentation, audits, roadmap, and archived TODOs
- `examples/` - examples and templates
- `.github/` - GitHub Actions workflows
