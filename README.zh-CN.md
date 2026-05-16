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

## 关键概念：User Assertion 用户确认问题

有时候 AI 不认为某个现象是问题，但用户知道结果是错的。Doctor link 允许用户明确标记：

> 这里就是问题。

这个用户确认的问题会成为一等诊断信号，并写入 AI 修复任务、测试记录、验证结果和 AI 协作检查中。

## 标准诊断包

Doctor link 生成并维护标准诊断包：

```text
DoctorReports/
└── <timestamp>_<project>_<issue>/
    ├── summary.md
    ├── problem-map.md
    ├── timeline.md
    ├── evidence-list.md
    ├── doctor-report.md
    ├── doctor-report.json
    ├── ai-context.json
    ├── reproduce-steps.md
    ├── ai-task.md
    ├── investigation-boundary.md
    ├── fix-verification-checklist.md
    ├── user-assertions.json
    ├── verification-result.json
    ├── ai-repair-result.json
    ├── diagnosis-history.json
    ├── assertion-compliance-report.json
    ├── repair-risk-review.json
    └── evidence/
```

## 常用命令

```bash
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link collect <package_dir> --project-root . --logs "logs/*.log" --command "python --version"
doctor-link verify <package_dir> --write-back
doctor-link assert <package_dir> --statement "这里就是问题"
doctor-link env --project-root . --out environment.json
doctor-link probe <file> --summary --out probe.json
doctor-link record <package_dir> --name "测试名称" --status partial --assertion-id assertion-1
doctor-link vly-proof <library> --package-dir <package_dir>
doctor-link compare before.json after.json --package-dir <package_dir>
doctor-link doctor-package <package_dir> --out DoctorReports/package.zip
doctor-link view <package_dir>
doctor-link view DoctorReports
doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ai-result <package_dir> --summary "AI 修复摘要" --claimed-fix "修复声明" --assertion-id assertion-1 --verification-step pytest
doctor-link diagnosis-history <package_dir> --ai-pass "第 1 轮 AI 诊断" --user-correction "用户修正" --evidence-id ev-1
doctor-link assertion-check <package_dir>
doctor-link risk-review <package_dir> --file doctor_link/cli.py --boundary doctor_link/
```

## P1 / P1+：证据采集与验证闭环

Doctor link 支持环境、日志、命令输出、媒体探测、附件、测试记录、Vly proof、修复前后对比和标准诊断包打包。

`doctor-link verify` 会生成：

- `verification-plan.md`
- `verification-result.json`

它不会只因为 AI 声称“已修复”就认定完成，而是会列出缺失证据、需要重跑的测试和下一步命令。

## P2 / P2+：本地诊断工作台

`doctor-link view` 提供本地只读诊断工作台，可浏览：

- summary / timeline / evidence；
- user assertions；
- AI task；
- verification；
- comparison；
- redaction / manifest；
- evidence 反向引用；
- assertion coverage；
- AI handoff blocks。

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

P3 生成并维护：

- `ai-repair-result.json` / `ai-repair-result.md`；
- `diagnosis-history.json` / `diagnosis-history.md`；
- `assertion-compliance-report.json` / `assertion-compliance-report.md`；
- `repair-risk-review.json` / `repair-risk-review.md`。

这些文件记录 AI 修复声明、诊断轮次、用户确认问题覆盖情况和修复风险。AI 输出只是协作记录，不是验证证据；问题是否完成仍以验证结果为准。

## 项目配置

项目可以在 `.doctorlink/` 中定义诊断规则：

```text
.doctorlink/
├── doctorlink.yml
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
- P3：AI Coding Collaboration Layer。

下一阶段是 P4：Automated Diagnosis Pipeline。

## 边界

以下操作需要单独授权：发布版本、创建 GitHub Release、发布到 PyPI、修改仓库权限、引入付费云服务、引入外部账号体系、改变 Doctor link 核心定位、把本地只读 Web UI 改成默认写回模式、启动 P6 实现开发。
