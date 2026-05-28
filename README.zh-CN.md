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

P5.9 不发布 GitHub Release，不创建 release tag，不发布 PyPI，不修改仓库权限，不引入付费云服务或外部账号体系，不启动 P6 实现开发。

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

Doctor link 当前已完成：

- P0：Diagnostic Foundation；
- P1：Evidence Collection Primitives；
- P1+：CLI Evidence Pipeline；
- P2：Local Read-only Diagnostic Workbench；
- P2+：Mainline Diagnostic Workbench Enhancements；
- P3：AI Coding Collaboration Layer；
- P4：Automated Diagnosis Pipeline；
- P5：Productization and Release Readiness；
- P5.9：Release Hardening and Usability Validation。

下一阶段是 P6：Diagnostic Protocol Standardization and Ecosystem Platform。P6 实现开发需要单独明确授权。

## 边界

以下操作需要单独授权：发布版本、创建 GitHub Release、发布到 PyPI、修改仓库权限、引入付费云服务、引入外部账号体系、改变 Doctor link 核心定位、把本地只读 Web UI 改成默认写回模式、启动 P6 实现开发。
