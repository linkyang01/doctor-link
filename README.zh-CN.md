# Doctor link

**语言 / Language：** [English](README.en.md) | 中文

Doctor link 是一个面向软件项目的人机协同诊断层。它服务于非程序员用户、开发者和 AI 编程工具，让人和 AI 可以围绕同一个问题、同一组证据、同一个验证标准进行协作。

Doctor link 不替代 Codex、Aider、OpenHands、Continue、Cursor 或其它 AI 编码工具。它的目标是为这些工具准备高质量的诊断上下文，让 AI 在修复问题时少猜、少乱改、可验证。

## 当前状态

Doctor link 已完成 P0-P6 的协议、Schema、产品化和生态规范工作，P7 已将前期规划中的本地运行能力转化为真实可执行、可测试、可文档化的 CLI 能力。

P5：Productization and Release Readiness 已完成。P6 实现开发需要单独明确授权，尤其是托管服务、外部账号、发布、真实签名密钥、marketplace 或企业集成行为。

P7.10 增加最终验证与收口层，包括 P7 runtime 验证脚本，以及覆盖 P7 命令面的 CI 校验。

Doctor link 仍然坚持本地优先。它不创建托管平台、不引入外部账号体系、不做遥测、不提供 marketplace、不创建 GitHub Release、不打 release tag、不发布到 PyPI。

## 核心定位

Doctor link 是 AI 编程工作流的诊断上下文层。

它坚持：

- 证据优先；
- 复现优先；
- 用户确认问题优先；
- AI 不得无证据忽略用户确认的问题；
- 修复必须验证；
- 本地优先、只读优先；
- 先协议和 CLI，后托管平台行为。

## 标准诊断包

Doctor link 在 `DoctorReports/` 下生成并维护标准诊断包，包含证据、时间线、用户确认问题、验证结果、AI 协作记录、工作流元数据、Schema 校验输出、流水线摘要、CI 报告、分发就绪报告、知识索引和归档记录。

## 常用命令

```bash
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link collect <package_dir> --project-root . --logs "logs/*.log" --command "python --version"
doctor-link verify <package_dir> --write-back
doctor-link assert <package_dir> --statement "这里就是问题"
doctor-link view <package_dir>
doctor-link view DoctorReports

doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ai-result <package_dir> --summary "AI 修复摘要" --claimed-fix "修复声明" --assertion-id assertion-1 --verification-step pytest
doctor-link diagnosis-history <package_dir> --ai-pass "第 1 轮 AI 诊断" --user-correction "用户修正" --evidence-id ev-1
doctor-link assertion-check <package_dir>
doctor-link risk-review <package_dir> --file doctor_link/cli.py --boundary doctor_link/

doctor-link strategy validate . --json
doctor-link reproduce list . --json
doctor-link reproduce run <reproduction_id> . --package-dir <package_dir> --json
doctor-link test list . --json
doctor-link test run . --job <job_id> --package-dir <package_dir> --json
doctor-link diagnose before --project "Demo" --summary "before issue" --out DoctorReports
doctor-link diagnose after --project "Demo" --summary "after fix" --before-package <before_package> --out DoctorReports
doctor-link diagnose compare <after_package> --json
doctor-link diagnose verify <after_package> --json
doctor-link schema validate <package_dir> --write --json
doctor-link conformance run <fixtures_root> --out DoctorReports/conformance --json
doctor-link health DoctorReports --json

doctor-link ci report DoctorReports --out DoctorReports/ci --json
doctor-link distribution check . --dist dist --out DoctorReports/distribution --json

doctor-link adapter list . --json
doctor-link adapter validate .doctorlink/adapters/demo-adapter/adapter.yml --json
doctor-link adapter run demo-adapter verification . --json

doctor-link plugin list . --json
doctor-link plugin validate .doctorlink/plugins/demo-plugin/plugin.yml --json
doctor-link plugin run demo-plugin verification . --json

doctor-link integrity manifest . --out DoctorReports/integrity-manifest.json --json
doctor-link integrity verify . DoctorReports/integrity-manifest.json --json
doctor-link privacy scan . --out DoctorReports/privacy-scan.json --json
doctor-link privacy redaction-gate . --out DoctorReports/redaction-gate.json --json
doctor-link privacy export-gate . --manifest DoctorReports/integrity-manifest.json --out DoctorReports/export-gate.json --json

doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json --json
doctor-link knowledge query DoctorReports/knowledge-index.json "missing evidence" --json
doctor-link knowledge export DoctorReports/knowledge-index.json DoctorReports/knowledge-export.json --json
doctor-link archive create DoctorReports DoctorReports/archive --metadata owner=qa --json
doctor-link archive inspect DoctorReports/archive --json
doctor-link archive policy-check DoctorReports/archive --max-files 1000 --json
doctor-link archive export DoctorReports/archive DoctorReports/archive.zip --json
```

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

- `docs/installation.md`
- `docs/quick-start.md`
- `docs/cli-reference.md`
- `docs/diagnostic-package-format.md`
- `docs/ai-coding-workflow.md`
- `docs/local-workbench.md`
- `docs/troubleshooting.md`
- `docs/privacy-model.md`
- `docs/product-overview.md`
- `docs/release-policy.md`
- `docs/usability-validation.md`
- `docs/e2e-validation.md`
- `docs/p5.9-final-audit.md`
- `docs/p5.10-local-validation.md`
- `docs/p6-schema-v1.md`
- `docs/p6-conformance.md`
- `docs/p6-adapter-sdk.md`
- `docs/p6-plugin-sdk.md`
- `docs/p6-ai-coding-integrations.md`
- `docs/p6-signing-integrity.md`
- `docs/p6-privacy-security.md`
- `docs/p6-enterprise-governance.md`
- `docs/p6-diagnostic-knowledge-base.md`
- `docs/p6-public-ecosystem-assets.md`
- `docs/p6-quality-closure.md`
- `docs/p7-final-audit.md`
- `docs/p7-self-validation.md`

## Runtime 覆盖范围

P7 已实现以下本地运行能力：

- 证据加固；
- 本地工作台加固；
- AI handoff runtime；
- CI 与运维自动化；
- 分发就绪检查；
- Adapter runtime；
- Plugin runtime；
- 完整性与隐私门禁；
- 本地知识索引；
- 本地归档辅助能力。

## 边界说明

Doctor link 当前不提供：

- 托管 Web 平台；
- 云同步；
- 外部账号体系；
- 遥测；
- marketplace；
- 真实签名密钥或密钥管理；
- 托管企业归档；
- 托管诊断知识库；
- 真实 RBAC 或企业身份集成；
- GitHub Release、release tag 或 PyPI 发布。
