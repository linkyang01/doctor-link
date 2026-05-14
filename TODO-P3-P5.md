# Doctor link P3-P5 TODO

本文件用于跟踪 Doctor link 后续 P3、P4、P5 的可执行任务。每完成一项，必须把对应任务从 `[ ]` 改为 `[x]`。

关联文件：

- P3 Issue: #18
- P4 Issue: #19
- P5 Issue: #20
- Roadmap: `docs/roadmap/p3-p5.md`
- ADR: `docs/adr/0005-p3-p5-roadmap.md`

---

## P3：AI Coding 协作增强

目标：让 Doctor link 成为用户、诊断包与 AI Coding 工具之间的结构化协作层。

### P3.1 AI 任务模板体系

- [ ] 定义 AI task template 数据模型
- [ ] 增加 bug fix 任务模板
- [ ] 增加 regression fix 任务模板
- [ ] 增加 investigation 任务模板
- [ ] 增加 refactor risk review 任务模板
- [ ] 增加 verification-only 任务模板
- [ ] 模板字段支持 evidence_ids
- [ ] 模板字段支持 user assertions
- [ ] 模板字段支持 reproduction steps
- [ ] 模板字段支持 investigation boundaries
- [ ] 模板字段支持 forbidden changes
- [ ] 模板字段支持 expected outputs
- [ ] 模板字段支持 verification steps
- [ ] 支持从指定模板生成 AI task
- [ ] 所有模板强制保留用户确认问题警示
- [ ] 增加模板渲染测试
- [ ] 更新 README.zh-CN.md
- [ ] 更新 README.en.md

### P3.2 AI 工具交付包

- [ ] 定义 AI tool handoff manifest 格式
- [ ] 增加 Codex handoff profile
- [ ] 增加 Cursor handoff profile
- [ ] 增加 Continue handoff profile
- [ ] 增加 Aider handoff profile
- [ ] 增加 OpenHands handoff profile
- [ ] 增加通用 Markdown / JSON handoff profile
- [ ] 新增 `doctor-link handoff <package_dir> --tool <tool>` 命令
- [ ] handoff 包含 ai-task
- [ ] handoff 包含 ai-context
- [ ] handoff 包含 evidence-list
- [ ] handoff 包含 user-assertions
- [ ] handoff 包含 investigation-boundary
- [ ] handoff 包含 verification-checklist
- [ ] 增加 handoff 测试
- [ ] 增加 CI smoke

### P3.3 AI 修复结果回填

- [ ] 定义 AI repair result schema
- [ ] 支持记录 files changed
- [ ] 支持记录 AI 修复摘要
- [ ] 支持记录 claimed fix
- [ ] 支持记录 risks
- [ ] 支持记录 assumptions
- [ ] 支持记录 evidence used
- [ ] 新增 `doctor-link ai-result <package_dir>` 命令
- [ ] 生成 `ai-repair-result.json`
- [ ] 生成 `ai-repair-result.md`
- [ ] AI 修复结果关联 user assertions
- [ ] AI 修复结果关联 verification steps
- [ ] 不把 AI 自称“已修复”当作验证证据
- [ ] 增加 AI repair result 测试
- [ ] 更新文档

### P3.4 多轮 AI 诊断上下文

- [ ] 定义 diagnosis round 数据模型
- [ ] 记录每轮 AI pass
- [ ] 记录每轮用户 correction
- [ ] 记录每轮新增 evidence
- [ ] 记录每轮 verification attempt
- [ ] 生成 `diagnosis-history.json`
- [ ] 生成 `diagnosis-history.md`
- [ ] 新增下一轮 AI task 上下文摘要命令
- [ ] 未解决的用户确认问题跨轮次保留
- [ ] 增加 diagnosis history 测试
- [ ] 更新文档

### P3.5 用户确认问题强制检查

- [ ] 增加 assertion compliance checker
- [ ] 检查 AI task 是否遗漏用户确认问题
- [ ] 检查 AI repair result 是否无证据忽略用户确认问题
- [ ] 对 unsupported dismissal 生成 warning
- [ ] 生成 `assertion-compliance-report.md`
- [ ] 新增 `doctor-link assertion-check <package_dir>` 命令
- [ ] assertion compliance 接入 verification status
- [ ] 增加 unsupported dismissal 测试
- [ ] 更新文档

### P3.6 修复风险评审

- [ ] 定义 repair risk checklist
- [ ] 支持识别 investigation boundary 外的变更
- [ ] 支持记录 risk level：low / medium / high / unknown
- [ ] 生成 `repair-risk-review.md`
- [ ] 新增 `doctor-link risk-review <package_dir>` 命令
- [ ] 增加 repair risk review 测试
- [ ] 更新文档

### P3.7 P3 质量保障与收尾

- [ ] 增加 P3 end-to-end smoke workflow
- [ ] 增加 sample AI handoff package fixture
- [ ] 增加 sample AI repair result fixture
- [ ] P2 Web UI 展示 AI handoff section
- [ ] P2 Web UI 展示 AI repair result section
- [ ] 更新 TODO.md / TODO-P3-P5.md
- [ ] P3 Issue #18 全部完成后关闭

---

## P4：自动化诊断与项目级工作流

目标：让 Doctor link 从手动诊断工具升级为项目级自动诊断流水线。

### P4.1 项目诊断策略

- [ ] 定义 `.doctorlink/diagnosis.yml`
- [ ] 支持 project type
- [ ] 支持 default commands
- [ ] 支持 evidence rules
- [ ] 支持 verification rules
- [ ] 支持 excluded paths
- [ ] 增加 diagnosis strategy 校验
- [ ] 新增 `doctor-link strategy validate` 命令
- [ ] 增加测试
- [ ] 更新文档

### P4.2 复现脚本管理

- [ ] 定义 reproduction script metadata 模型
- [ ] 新增 `.doctorlink/reproduce.yml`
- [ ] 支持 manual reproduction entry
- [ ] 支持 command-based reproduction entry
- [ ] 支持 test-based reproduction entry
- [ ] 新增 `doctor-link reproduce list` 命令
- [ ] 新增 `doctor-link reproduce run <id>` 命令
- [ ] reproduction output 写入诊断包 evidence
- [ ] 增加测试
- [ ] 更新文档

### P4.3 测试矩阵自动化

- [ ] 扩展 `.doctorlink/test-matrix.yml` 支持 executable test jobs
- [ ] 定义 test job status 模型
- [ ] 新增 `doctor-link test run` 命令
- [ ] test result 写入 `evidence/test-results/`
- [ ] test result 关联 verification checklist
- [ ] 增加测试
- [ ] 更新文档

### P4.4 before / after 诊断包自动生成

- [ ] 定义 before / after workflow
- [ ] 新增 `doctor-link diagnose before` 命令
- [ ] 新增 `doctor-link diagnose after` 命令
- [ ] before / after 包命名可追踪
- [ ] before / after 包 metadata 可关联
- [ ] 自动保留 before report 路径用于 comparison
- [ ] 增加测试
- [ ] 更新文档

### P4.5 自动 comparison 与 verification

- [ ] 新增 `doctor-link diagnose compare` 命令
- [ ] 新增 `doctor-link diagnose verify` 命令
- [ ] after package 后可自动 run compare
- [ ] after package 后可自动 run verify
- [ ] 生成 pipeline summary report
- [ ] 缺少验证证据时不得标记 success
- [ ] 增加测试
- [ ] 更新文档

### P4.6 GitHub Actions 与 PR 集成

- [ ] 增加 reusable GitHub Actions example workflow
- [ ] 增加 PR diagnostic check mode
- [ ] 支持上传 diagnostic package artifacts
- [ ] 支持 PR comment summary 草稿
- [ ] 失败时指向 diagnostic package artifact
- [ ] 增加 workflow syntax 校验
- [ ] 更新文档

### P4.7 项目健康度看板基础

- [ ] 定义 project health summary 模型
- [ ] 统计 package count
- [ ] 统计 unresolved assertions
- [ ] 统计 failed verifications
- [ ] 统计 recent regressions
- [ ] 生成 `project-health.json`
- [ ] 生成 `project-health.md`
- [ ] P2 Web UI 增加 project health 面板
- [ ] 增加测试
- [ ] 更新文档

### P4.8 P4 质量保障与收尾

- [ ] 增加 P4 end-to-end fixture project
- [ ] 增加 pipeline smoke tests
- [ ] 增加 broken reproduction 场景测试
- [ ] 增加 failed test 场景测试
- [ ] 增加 missing evidence 场景测试
- [ ] 更新 README.zh-CN.md
- [ ] 更新 README.en.md
- [ ] 更新 TODO.md / TODO-P3-P5.md
- [ ] P4 Issue #19 全部完成后关闭

---

## P5：产品化、生态与发布准备

目标：让 Doctor link 具备可安装、可文档化、可交付、可发布准备的产品形态。

### P5.1 版本与发布策略

- [ ] 定义 semantic versioning policy
- [ ] 新增 `CHANGELOG.md`
- [ ] 新增 release checklist 文档
- [ ] 明确无授权不得发布版本
- [ ] 增加 version consistency CI 检查

### P5.2 打包与安装

- [ ] 完善 `pyproject.toml` metadata
- [ ] 增加 license metadata
- [ ] 增加 classifiers
- [ ] 增加 package data rules
- [ ] 测试 source install
- [ ] 测试 wheel build
- [ ] 增加 packaging CI job
- [ ] 编写安装文档

### P5.3 用户文档

- [ ] 新增 quick start guide
- [ ] 新增 CLI command reference
- [ ] 新增 diagnostic package format guide
- [ ] 新增 AI coding workflow guide
- [ ] 新增 P2 local workbench guide
- [ ] 新增 troubleshooting guide
- [ ] 新增中英文文档一致性检查清单

### P5.4 示例与模板

- [ ] 新增 example diagnostic package
- [ ] 新增 example project with `.doctorlink` config
- [ ] 新增 example AI handoff package
- [ ] 新增 example before / after comparison
- [ ] 新增 example verification result
- [ ] 新增 template gallery 文档

### P5.5 安全与隐私审查

- [ ] 编写 privacy model 文档
- [ ] 编写 sensitive information handling 文档
- [ ] 复核 redaction defaults
- [ ] 新增 exported package security checklist
- [ ] 说明 diagnostic package 可能包含哪些信息
- [ ] 增加 redaction regression tests

### P5.6 产品定位与官网文档

- [ ] 新增 product overview page
- [ ] 新增 non-programmer user use case
- [ ] 新增 AI coding tool use case
- [ ] 新增 developer use case
- [ ] 新增 team workflow use case
- [ ] 新增 architecture overview diagram source
- [ ] 新增 roadmap document
- [ ] 新增 contribution guide
- [ ] 新增 issue triage guide

### P5.7 Adapter 与插件文档

- [ ] 说明 adapter 概念
- [ ] 说明 collector extension points
- [ ] 说明 handoff profile extension points
- [ ] 说明项目级 `.doctorlink` customization
- [ ] 增加 future SDK placeholder docs，避免过度承诺实现

### P5.8 发布准备但不发布

- [ ] 准备 draft release notes
- [ ] 准备 draft GitHub Release body
- [ ] 确认全部测试通过
- [ ] 确认文档已更新
- [ ] 确认示例可运行
- [ ] 确认无已知 critical privacy gaps
- [ ] 未获明确授权前停止发布
- [ ] P5 Issue #20 全部完成后关闭
