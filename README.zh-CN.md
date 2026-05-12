# Doctor link

**语言 / Language：** [English](README.en.md) | 中文

Doctor link 是一个面向软件项目的人机协同诊断层。

它服务于非程序员用户、开发者和 AI 编程工具，让人和 AI 可以围绕同一个问题、同一组证据、同一个验证标准进行协作。

Doctor link 不替代 Codex、Aider、OpenHands、Continue 或其它 AI 编码工具。它要做的是为这些工具准备高质量的诊断上下文，让 AI 在修复问题时少猜、少乱改、可验证。

## 它解决什么问题？

AI 编程工具在任务明确时很强，但当问题描述模糊、缺少运行时证据、缺少用户真实判断时，就容易误判。

典型的模糊描述是：

> 这个不能用。

Doctor link 要把它变成结构化诊断包：

- 发生了什么；
- 发生在哪里；
- 如何复现；
- 期望结果是什么；
- 实际结果是什么；
- 有哪些证据；
- 用户确认的问题是什么；
- 应该优先调查什么；
- 不应该乱改什么；
- 修复后如何验证。

## 核心定位

Doctor link 不是日志查看器，也不是提示词生成器。

它的定位是：

> AI 编程工作流的诊断上下文层。

它提供：

- 证据采集；
- 复现记录；
- 时间线构建；
- 问题地图；
- 用户确认问题保留；
- AI 修复任务生成；
- 修复验证计划；
- 修复前后诊断报告对比。

## 关键概念：User Assertion 用户确认问题

Doctor link 的关键能力是 `User Assertion`。

有时候 AI 不认为某个现象是问题。例如程序没有崩溃，但用户知道结果是错的。

Doctor link 允许用户明确标记：

> 这里就是问题。

这个用户确认的问题会成为一等诊断信号，并写入 AI 修复任务。

生成的 AI 任务必须包含：

> 用户已确认这是问题。不要在没有证据的情况下把它判断为正常行为。

## 五层地基架构

Doctor link 采用五层架构：

```text
Layer 1: Diagnostic Protocol 诊断协议层
Layer 2: Evidence Collection 证据采集层
Layer 3: Human Diagnosis Surface 人类诊断层
Layer 4: AI Collaboration Package AI 协作层
Layer 5: Fix Verification Loop 修复验证闭环
```

### Layer 1：Diagnostic Protocol 诊断协议层

核心模型：

- DiagnosticEvent
- DiagnosticPackage
- EvidenceItem
- TimelineStep
- UserAssertion
- ProblemMap
- AITask
- VerificationChecklist

### Layer 2：Evidence Collection 证据采集层

采集内容：

- 系统环境；
- 日志；
- 命令输出；
- 测试结果；
- 文件与附件；
- 截图；
- 外部工具输出。

### Layer 3：Human Diagnosis Surface 人类诊断层

给人看的输出：

- summary.md
- problem-map.md
- timeline.md
- evidence-list.md
- user-assertions.json

### Layer 4：AI Collaboration Package AI 协作层

给 AI / Codex 看的输出：

- ai-context.json
- ai-task.md
- investigation-boundary.md
- fix-verification-checklist.md

### Layer 5：Fix Verification Loop 修复验证闭环

修复验证输出：

- before-report.json
- after-report.json
- regression-result.json
- Go / No-Go 结论

## 标准诊断包

每次诊断应生成如下结构：

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
    └── evidence/
        ├── environment.json
        ├── logs/
        ├── screenshots/
        ├── command-output/
        ├── test-results/
        └── attachments/
```

## 运行模式

Doctor link 支持三种诊断模式。

### 1. External Mode 外部诊断模式

Doctor link 在目标程序外部运行，收集项目文件、日志、命令输出、环境信息和用户确认问题。

这是第一版优先实现的模式。

### 2. Sidecar Mode 伴随运行模式

Doctor link 与目标程序同时运行，监听日志、进程状态、文件变化、测试执行过程和手动失败标记。

### 3. Embedded SDK Mode 嵌入式 SDK 模式

目标程序可以选择接入轻量 SDK，主动上报结构化运行时事件。

该模式是可选增强，不应成为 Doctor link 可用的前提。

## 项目配置

项目可以在 `.doctorlink/` 中定义诊断规则：

```text
.doctorlink/
├── doctorlink.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

## 第一个真实场景：Vly

Vly 是 Doctor link 的第一个真实应用场景。

Doctor link 将帮助 Vly 验证它是否能成为全能媒体播放器，重点测试：

- 全格式播放；
- 原盘播放；
- 字幕；
- 音轨；
- 本地模拟 NAS；
- 播放失败诊断；
- 用户确认的播放问题；
- 是否进入下一阶段的 Go / No-Go 判断。

## 规划命令

```bash
doctor-link init
doctor-link scan
doctor-link report
doctor-link assert
doctor-link ai-task
doctor-link verify-plan
```

## 当前状态

Doctor link 当前处于地基建设阶段。

当前优先实现：

1. 核心数据模型；
2. 标准诊断包生成；
3. 用户确认问题支持；
4. 问题地图生成；
5. AI 任务生成；
6. 修复验证清单生成；
7. `.doctorlink/` 配置模板。

## 第一版成功标准

第一版真正成功，不是命令能跑，而是能完成以下闭环：

1. 用户报告或选择一个问题；
2. Doctor link 创建标准诊断包；
3. 用户标记确认的问题；
4. Doctor link 生成问题地图；
5. Doctor link 生成 AI 可执行的修复任务；
6. AI 任务包含证据、边界和验证步骤；
7. Doctor link 生成修复验证清单；
8. 修复前后诊断报告可以对比。
