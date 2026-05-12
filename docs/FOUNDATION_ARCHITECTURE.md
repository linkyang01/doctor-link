# Doctor link 地基架构设计

## 1. 重新定位

Doctor link 不是普通日志工具，也不是简单的 AI Prompt 生成器。

Doctor link 的核心定位是：

> Human-AI Shared Diagnosis Layer

中文可以理解为：

> 人和 AI 共用的软件诊断协作层。

它位于用户、项目、测试、日志、AI Code / Codex 之间，负责把模糊问题转化为可复现、可验证、可交给 AI 修复的结构化诊断包。

## 2. 为什么需要这个地基

AI 编码工具在大项目里容易失效，核心原因不是不会写代码，而是缺少完整问题现场。

它们经常缺少：

- 运行环境；
- 复现步骤；
- 用户操作时间线；
- 输入数据；
- 关键日志；
- 外部工具输出；
- 用户确认的问题；
- 调查边界；
- 修复后验证标准。

Doctor link 的任务是补足这些缺失上下文。

## 3. 参考项目吸收原则

Doctor link 不复制单一项目，而是吸收成熟项目的有效机制。

| 参考方向 | 吸收能力 | Doctor link 落点 |
|---|---|---|
| Sentry / GlitchTip | 错误事件、版本、环境、聚合 | DiagnosticEvent |
| sosreport | 一次性证据包 | DiagnosticPackage |
| OpenTelemetry | logs / metrics / traces / events | Signals 分层 |
| Playwright Trace | 操作时间线、失败定位 | Timeline / Reproduction |
| Repomix | AI 上下文打包 | AI Context Packager |
| OSV Scanner | 扫描、风险等级、结构化结果 | Status / Severity / Confidence |
| AI Code 工具 | 代码修改能力 | Doctor link 只提供诊断上下文 |

## 4. 总体架构

```text
Doctor link
├── Core Engine
│   ├── DiagnosticEvent
│   ├── DiagnosticPackage
│   ├── EvidenceCollector
│   ├── TimelineRecorder
│   ├── FailureClassifier
│   ├── ProblemMapBuilder
│   ├── UserAssertionManager
│   ├── HumanOverrideManager
│   ├── AIContextPackager
│   └── FixVerifier
│
├── Adapters
│   ├── GenericAdapter
│   ├── VlyAdapter
│   ├── PythonAdapter
│   ├── NodeAdapter
│   └── MacAppAdapter
│
├── Connectors
│   ├── CommandRunner
│   ├── FileCollector
│   ├── GitHubConnector
│   ├── CodexTaskConnector
│   └── ExternalToolConnector
│
├── Outputs
│   ├── MarkdownReports
│   ├── JsonReports
│   ├── AI Tasks
│   ├── Problem Maps
│   └── Verification Checklists
│
└── Interfaces
    ├── CLI
    ├── Local Web UI
    └── Future Desktop UI
```

## 5. 核心边界

Doctor link 不做：

- 不直接替代 Codex；
- 不直接替代 IDE；
- 不负责自动修代码；
- 不替代完整监控平台；
- 不强制绑定某一种编程语言；
- 不只服务 Vly。

Doctor link 要做：

- 收集证据；
- 记录复现；
- 生成问题地图；
- 保留用户确认问题；
- 生成 AI 可执行任务；
- 生成修复验证清单；
- 对比修复前后结果。

## 6. 核心数据模型

### 6.1 DiagnosticEvent

一次问题现场。

```text
DiagnosticEvent
├── event_id
├── project
├── adapter
├── occurred_at
├── severity
├── category
├── summary
├── environment
├── timeline
├── evidence
├── reproduce_steps
├── user_assertions
├── diagnosis
├── ai_task
└── verification_checklist
```

### 6.2 DiagnosticPackage

一次诊断产物包。

```text
DiagnosticPackage
├── package_id
├── event_id
├── root_dir
├── markdown_reports
├── json_reports
├── evidence_dir
├── ai_context
├── ai_task
├── verification_checklist
└── status
```

### 6.3 UserAssertion

用户确认的问题信号。

```text
UserAssertion
├── assertion_id
├── report_id
├── created_at
├── severity
├── user_statement
├── expected_behavior
├── actual_behavior
├── related_step
├── related_evidence
├── ai_disagreed_or_missed
├── investigation_scope
├── locked_scope
└── next_ai_instruction
```

### 6.4 ProblemMap

人类可读的问题地图。

```text
ProblemMap
├── user_symptom
├── failure_stage
├── evidence
├── possible_root_causes
├── ruled_out_causes
├── related_modules
├── human_confirmed_problem
└── next_action
```

## 7. 标准输出目录

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

## 8. 核心工作流

### 8.1 AI 正常能定位时

```text
用户发现问题
↓
Doctor link 采集证据
↓
Doctor link 生成诊断包
↓
AI / Codex 读取诊断包
↓
AI 修改代码
↓
Doctor link 执行验证清单
↓
输出修复前后对比
```

### 8.2 AI 找不到问题时

```text
AI 初步分析失败
↓
用户打开 Human Diagnosis View
↓
用户查看 Problem Map / Timeline / Evidence
↓
用户标记问题点或关键证据
↓
Doctor link 生成 UserAssertion
↓
Doctor link 重新生成聚焦 AI 任务
↓
AI 再次修复
```

### 8.3 AI 不认为是问题时

```text
AI 判断正常
↓
用户确认这是问题
↓
Doctor link 记录 Human Override
↓
AI 任务中明确写入：用户已确认这是问题，不得无证据忽略
↓
AI 按用户确认的问题重新调查
```

## 9. doctorlink.yml 配置协议

每个项目可以通过 `doctorlink.yml` 声明诊断规则。

```yaml
project:
  name: Vly
  type: macos-media-player

collect:
  environment:
    - system
    - app_version
    - dependencies
  logs:
    - ~/Library/Logs/Vly/*.log
  commands:
    - ffprobe -version
    - mediainfo --Version

tests:
  playback_matrix:
    - mkv_hevc_dts
    - bdmv_main_movie
    - pgs_subtitle

ai:
  boundaries:
    - do not rewrite UI unless evidence points to UI
    - do not replace playback engine without evidence
  verification:
    - rerun failed samples
    - compare doctor reports
```

## 10. 第一阶段必须完成的地基

### P0 数据模型

- DiagnosticEvent
- DiagnosticPackage
- EvidenceItem
- TimelineStep
- UserAssertion
- ProblemMap
- AITask
- VerificationChecklist

### P0 文件结构

- 标准报告目录生成器；
- Markdown 输出；
- JSON 输出；
- evidence 证据目录；
- user-assertions.json。

### P0 命令

```bash
doctor-link init
doctor-link scan
doctor-link report
doctor-link assert
doctor-link ai-task
doctor-link verify-plan
```

### P1 能力

- environment_collector；
- command_runner；
- media_probe；
- test_recorder；
- problem_map_builder；
- user_assertion_manager。

## 11. 第一版成功标准

Doctor link 第一版成功，不是命令能跑，而是能完成一次完整闭环：

1. 用户输入一个问题；
2. 工具生成诊断包；
3. 用户能标记“这里就是问题”；
4. 工具生成 AI 任务；
5. AI 有明确证据和边界；
6. 修复后有验证清单；
7. 报告能对比修复前后。

## 12. 产品原则

- 证据优先；
- 用户确认问题优先；
- AI 不得无证据忽略用户确认的问题；
- 复现步骤必须保留；
- 修复边界必须明确；
- 修复后必须验证；
- 所有输出同时支持人读和机器读；
- 地基要稳定，后续适配器可以扩展。
