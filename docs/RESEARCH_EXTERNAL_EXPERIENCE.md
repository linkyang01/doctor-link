# Doctor link 外部经验与科研想法整理

## 1. 整理目标

本文件用于把外部成熟工程经验、AI Coding 项目经验、事故响应经验、Bug Report 研究、调试研究和 AI Agent 可观测性思路，整理成 Doctor link 的产品与技术设计依据。

Doctor link 的目标不是做一个普通日志工具，而是做一个面向 AI Code / Codex / 非程序员用户的软件诊断协作层。

## 2. 外部经验总结

### 2.1 Bug Report 研究：复现步骤、实际结果、期望结果很关键

软件工程研究长期指出，Bug 报告质量会直接影响修复效率。高质量 Bug 报告通常包含：

- 问题描述；
- 复现步骤；
- 实际结果；
- 期望结果；
- 环境信息；
- 崩溃堆栈；
- 附件或日志。

Doctor link 应把这些内容产品化，不能让用户手工乱写。

落地需求：

- reproduce-steps.md；
- expected_behavior；
- actual_behavior；
- environment.json；
- evidence-list.md；
- user-assertions.json。

### 2.2 Scientific Debugging：用假设、证据、实验来找 Bug

自动化调试研究强调，调试应该像科学实验一样：提出假设、收集证据、验证或否定假设。

Doctor link 应支持：

- hypothesis；
- evidence；
- experiment；
- result；
- ruled_out_causes；
- next_action。

落地需求：

- problem-map.md 中加入“可能原因”和“已排除原因”；
- AI 任务要求不能无证据猜测；
- 修复必须有验证清单。

### 2.3 AI Coding Agent 研究：AI 缺少运行时证据和调试工具

AI Coding Agent 在修 Bug 时常常依赖静态代码阅读和反复试错。外部研究和项目都说明，运行时证据、交互式调试、测试结果和日志会显著提升 AI 修复能力。

Doctor link 应成为 AI Coding Agent 的诊断输入层。

落地需求：

- command-output；
- runtime logs；
- timeline；
- test-results；
- before / after report；
- fix-verification-checklist.md。

### 2.4 AI Agent 可观测性：要知道 Agent 做了什么

AI Agent 调试领域强调：只看最终输出不够，必须记录 LLM 调用、工具调用、错误、循环、上下文漂移和决策过程。

Doctor link 可吸收这种思路，但面向更通用的软件诊断。

落地需求：

- signals/events；
- timeline；
- ai-context.json；
- AI 任务生成记录；
- 修复前后对比。

### 2.5 Incident Response / Postmortem：时间线、证据、复盘、行动项

成熟事故响应流程强调：事故处理不只是恢复服务，还要记录时间线、证据、影响、原因、行动项和复盘状态。

Doctor link 应把单个软件 Bug 也当成一个小型 incident 管理。

落地需求：

- 诊断状态：Draft / In Review / AI Ready / Fixing / Verifying / Closed / Reopened；
- timeline.md；
- follow-up actions；
- owner / reviewer；
- Go / No-Go。

### 2.6 Session Replay：问题现场比日志更重要

用户行为回放类项目强调“用户实际做了什么”。这对 Doctor link 很重要，因为很多问题不是程序崩溃，而是用户体验不符合预期。

Doctor link 不一定第一版做录屏，但必须做“事件时间线”。

落地需求：

- TimelineStep；
- action；
- target；
- result；
- evidence；
- user_marked_failure_point。

### 2.7 AI Code 项目经验：诊断规则和检查规则要文件化

AI 编码工具正在走向规则化、仓库化、CI 化。Doctor link 也应该把诊断规则文件化，而不是只靠临时 prompt。

落地需求：

```text
.doctorlink/
├── doctorlink.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

### 2.8 Agent Native Observability：让编码 Agent 获取观测上下文

外部趋势正在把 observability 接入 Claude Code、Cursor 等编码 Agent，使 Agent 可以直接读取 traces、logs、metrics、部署历史和代码上下文。

Doctor link 的定位与此互补：

- 对云服务：接入 observability；
- 对本地软件 / 自用项目：生成诊断包；
- 对非程序员：提供问题地图和用户确认问题；
- 对 AI：输出结构化上下文。

## 3. 科研想法：Doctor link 可以做成什么

### 3.1 AI-native Diagnostic Package

Doctor link 的核心产物不是日志，而是 AI 原生诊断包。

它包含：

- 人类可读总结；
- 机器可读 JSON；
- 证据目录；
- 时间线；
- 用户确认问题；
- AI 任务；
- 修复验证清单。

### 3.2 Human Assertion as First-class Signal

用户确认的问题应作为一等信号。

当 AI 认为“正常”，但用户确认“这就是问题”，Doctor link 必须保存并传递该判断。

### 3.3 Diagnosis Protocol before UI

Doctor link 应先定义诊断协议，再做界面。

核心协议包括：

- DiagnosticEvent；
- DiagnosticPackage；
- EvidenceItem；
- TimelineStep；
- UserAssertion；
- ProblemMap；
- AITask；
- VerificationChecklist。

### 3.4 Fix Verification Loop

AI 修复后必须回到 Doctor link 验证。

闭环为：

```text
诊断前报告
↓
AI 修复任务
↓
代码修改
↓
复测
↓
诊断后报告
↓
前后对比
```

### 3.5 Doctor link as AI Coding Guardrail

Doctor link 可以成为 AI Coding 的约束层：

- 不允许无证据猜测；
- 不允许忽略用户确认问题；
- 不允许无验证宣布修复；
- 不允许无限扩大修改范围；
- 必须说明证据、范围和验证方式。

## 4. 对 Doctor link 的设计更新

### 4.1 产品定位

Doctor link 是：

> 面向 AI Code / Codex / 非程序员用户的人机协同诊断工具。

它不是：

- 普通日志查看器；
- 普通测试工具；
- 普通 prompt 工具；
- AI 编码工具的替代品。

### 4.2 核心用户

- 非程序员项目负责人；
- AI Coding 用户；
- 开发者；
- 自用软件项目维护者；
- AI Agent 工具使用者。

### 4.3 核心产物

```text
summary.md
problem-map.md
timeline.md
evidence-list.md
doctor-report.md
doctor-report.json
ai-context.json
reproduce-steps.md
ai-task.md
fix-verification-checklist.md
user-assertions.json
evidence/
```

## 5. 下一步落地优先级

### P0：诊断协议

- DiagnosticEvent；
- DiagnosticPackage；
- EvidenceItem；
- TimelineStep；
- UserAssertion；
- ProblemMap；
- AITask；
- VerificationChecklist。

### P0：标准诊断包

- package_builder.py；
- 标准目录生成；
- JSON 输出；
- Markdown 输出。

### P0：人工确认问题

- user_assertion_manager.py；
- user-assertions.json；
- AI task 中强制写入用户确认问题。

### P0：问题地图

- problem_map_builder.py；
- problem-map.md。

### P1：运行证据

- environment_collector.py；
- command_runner.py；
- log_collector.py；
- media_probe.py。

### P1：修复验证

- verification_builder.py；
- before / after report；
- regression-result.json。

### P1：项目配置

- .doctorlink/doctorlink.yml；
- .doctorlink/test-matrix.yml；
- .doctorlink/assertions.yml；
- .doctorlink/verification.yml。

## 6. 对 Vly 的直接影响

Vly 的全能播放器验证应成为 Doctor link 的第一套真实诊断场景。

Doctor link 需要帮 Vly 回答：

1. 哪个文件不能播？
2. 失败发生在哪一步？
3. ffprobe / MediaInfo 是否能识别？
4. 是视频、音频、字幕、原盘、路径还是播放器底座问题？
5. 用户是否确认“播放不完整也是失败”？
6. AI 修复后如何复测？

## 7. 最终设计原则

1. 证据优先；
2. 复现优先；
3. 用户确认问题优先；
4. AI 不得无证据忽略用户判断；
5. 任务必须有边界；
6. 修复必须可验证；
7. 诊断规则必须文件化；
8. 报告必须人能看、AI 能读、工具能解析；
9. Doctor link 不修代码，只让 AI 修得更准；
10. 先地基，后界面。
