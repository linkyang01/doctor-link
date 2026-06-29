# Doctor link

**语言 / Language：** [English](README.en.md) | 中文

Doctor link 是一个面向软件项目的人机协同诊断层。它服务于非程序员用户、开发者和 AI 编程工具，让人和 AI 可以围绕同一个问题、同一组证据、同一个验证标准进行协作。

Doctor link 不替代 Codex、Aider、OpenHands、Continue、Cursor 或其它 AI 编码工具。它的目标是为这些工具准备高质量的诊断上下文，让 AI 在修复问题时少猜、少乱改、可验证。

## 当前状态

Doctor link 已完成 P0-P6 的协议、Schema、产品化和生态规范工作，P7 已将前期规划中的本地运行能力转化为真实可执行、可测试、可文档化的 CLI 能力。Post-P7 加固修复也已完成。

P5：Productization and Release Readiness 已完成。P6 实现开发需要单独明确授权，尤其是托管服务、外部账号、发布、真实签名密钥、marketplace 或企业集成行为。

P7.10 增加最终验证与收口层，包括 P7 runtime 验证脚本，以及覆盖 P7 命令面的 CI 校验。

Doctor link 仍然坚持本地优先。最新 GitHub 正式版（`v0.1.2`，Latest，2026-06-29）已发布，含 wheel 与 sdist 资产。它不创建托管平台、不引入外部账号体系、不做遥测、不提供 marketplace。PyPI 发布为可选项。

## 常用命令

```bash
doctor-link wizard --folder . --tool cursor
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link verify <package_dir> --write-back
doctor-link handoff list
doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ci report DoctorReports --out DoctorReports/ci --json
doctor-link distribution check . --dist dist --out DoctorReports/distribution --json
doctor-link adapter run demo-adapter verification . --allow-run --json
doctor-link plugin run demo-plugin verification . --allow-run --json
doctor-link integrity verify . DoctorReports/integrity-manifest.json --strict --json
doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json --json
doctor-link archive create DoctorReports-source DoctorReports/archive --metadata owner=qa --json
```

Adapter 和 Plugin 的 `run` 命令默认只做 dry-run，不执行配置的本地命令。默认模式会校验 manifest 并写入运行/审计记录。只有在用户审查 manifest 后显式传入 `--allow-run`，才会真正执行本地命令。

## 验证入口

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link
python -m build
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

## 文档入口

- `../installation.md`
- `../quick-start.md`
- `../cli-reference.md`
- `../project-status.md`
- `../p7-final-audit.md`
- `../p7-self-validation.md`
- `../acceptance-review.md`
- `../archive/completed-todos/README.md`

## Runtime 覆盖范围

P7 已实现证据加固、本地工作台加固、AI handoff runtime、CI 自动化、分发就绪检查、Adapter runtime、Plugin runtime、完整性与隐私门禁、本地知识索引、本地归档辅助能力。

## 边界说明

Doctor link 当前不提供托管 Web 平台、云同步、外部账号体系、遥测、marketplace、真实签名密钥或密钥管理、托管企业归档、托管诊断知识库或真实 RBAC。PyPI 发布仍为可选项。
