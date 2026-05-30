# Doctor link

**语言 / Language：** [English](README.en.md) | 中文

Doctor link 是一个面向软件项目的人机协同诊断层。它服务于非程序员用户、开发者和 AI 编程工具，让人和 AI 可以围绕同一个问题、同一组证据、同一个验证标准进行协作。

Doctor link 不替代 Codex、Aider、OpenHands、Continue、Cursor 或其它 AI 编码工具。它的目标是为这些工具准备高质量的诊断上下文，让 AI 在修复问题时少猜、少乱改、可验证。

## 核心定位

Doctor link 是 AI 编程工作流的诊断上下文层。

它坚持：

- 证据优先；
- 复现优先；
- 用户确认问题优先；
- AI 不得无证据忽略用户确认的问题；
- 修复必须验证；
- 本地优先、只读优先；
- 先协议和 CLI，后 Web UI。

## 标准诊断包

Doctor link 在 `DoctorReports/` 下生成并维护标准诊断包，包含证据、时间线、用户确认问题、验证结果、AI 协作记录、工作流元数据和自动诊断流水线摘要。

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

## P1 / P1+：证据采集与验证闭环

Doctor link 支持环境、日志、命令输出、媒体探测、附件、测试记录、Vly proof、修复前后对比和标准诊断包打包。

`doctor-link verify` 会生成：

- `verification-plan.md`
- `verification-result.json`

它不会只因为 AI 声称“已修复”就认定完成，而是会列出缺失证据、需要重跑的测试和下一步命令。

## P2 / P2+：本地诊断工作台

`doctor-link view` 提供本地只读诊断工作台，可浏览 summary、timeline、evidence、user assertions、AI task、verification、comparison、redaction、manifest 和 AI handoff blocks。

P2 Web UI 默认只读，不做云同步、不做账号体系、不默认写回诊断包。

## P3：AI Coding 协作层

P3 已完成 AI Coding 协作能力：

- AI task template；
- AI tool handoff package；
- `doctor-link handoff`；
- `doctor-link ai-result`；
- `doctor-link diagnosis-history`；
- `doctor-link assertion-check`；
- `doctor-link risk-review`。

AI 输出只是协作记录，不是验证证据；问题是否完成仍以验证结果为准。

## P4：自动化诊断流水线

P4 已完成本地自动化诊断流水线能力：

- 基于 `.doctorlink/diagnosis.yml` 的诊断策略校验；
- 基于 `.doctorlink/reproduce.yml` 的复现管理；
- 基于 `.doctorlink/test-matrix.yml` 的可执行测试矩阵；
- before / after 诊断包工作流；
- 自动 comparison 与 verification；
- GitHub Actions PR diagnostics 文档与 workflow 示例；
- 项目健康度摘要。

当验证证据缺失时，pipeline success 保持 false，不会误判为成功。

## P5：产品化与发布准备

P5 已完成产品化和发布准备，但没有执行发布：

- 语义化版本与发布策略；
- `CHANGELOG.md` 与 release checklist；
- 包元数据、License 和安装指南；
- 用户文档与示例模板；
- 隐私与安全审查；
- 产品定位与贡献文档；
- Adapter 与扩展文档；
- draft release notes 和 draft GitHub Release body。

P5 不创建 GitHub Release，不打 release tag，不发布到 PyPI。

## P5.9：发布加固与可用性验证

P5.9 已完成发布前加固和可用性验证收尾：

- wheel 与 sdist 构建验证；
- 已安装 wheel 的 CLI smoke 验证；
- ruff 静态检查；
- pytest coverage 报告；
- 一键本地可用性验证脚本；
- E2E 验证脚本；
- CLI 入口关系审查；
- P5.9 final audit。

可用性验证入口：

```bash
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
```

## P5.10：P6 授权前验证加固

P5.10 已建立完整验证门槛，并已通过 GitHub Actions 云端验证和 Doctor link 自检验证。

本地目标环境验证仍然可选，适用于需要在指定 Mac、工作站或交付环境证明运行结果的场景。

## P6：诊断协议标准化与生态规范

P6 已完成 P6.1-P6.11 的规划、schema、规范、兼容性、生态资产和质量收口文档。

已完成：

- P6.1 Diagnostic Package Schema v1；
- P6.2 Compatibility and conformance test suite；
- P6.3 Adapter SDK planning；
- P6.4 Plugin SDK planning；
- P6.5 Third-party AI Coding integration specification；
- P6.6 Diagnostic package signing and integrity；
- P6.7 Privacy and security level specification；
- P6.8 Enterprise archive and governance model；
- P6.9 Cross-project diagnostic knowledge base；
- P6.10 Public ecosystem assets；
- P6.11 P6 quality and closure。

P6 当前是规范与 schema 收口，不代表已实现 Web 平台、云服务、账号体系、市场平台、真实第三方集成、真实签名、真实权限系统、企业归档系统、真实知识库服务、Adapter SDK 运行时或 Plugin SDK 运行时。

## 项目配置

项目可以在 `.doctorlink/` 中定义诊断规则：

```text
.doctorlink/
├── doctorlink.yml
├── diagnosis.yml
├── reproduce.yml
├── collect.yml
├── package.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

命令行参数优先级高于配置文件。

## 当前状态

Doctor link 当前已完成 P0-P5.10 主线能力和 P6.1-P6.11 规划规范收口。

未执行：

- GitHub Release；
- release tag；
- PyPI 发布；
- Web 平台；
- 云服务；
- 账号体系；
- 市场平台；
- Adapter SDK 运行时；
- Plugin SDK 运行时。