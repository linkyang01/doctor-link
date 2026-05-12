# Doctor link 参考项目需求合并

本文件把成熟项目中有价值的诊断能力合并为 Doctor link 的正式需求。Doctor link 不复制某一个项目，而是把错误追踪、系统诊断、测试追踪、结构化报告和 AI 上下文打包组合起来，形成真正可用的通用诊断工具。

## 1. 可借鉴能力

### Sentry / GlitchTip：错误事件模型

Doctor link 需要统一的 Diagnostic Event，用来描述一次问题现场。

建议字段：

- event_id
- project
- adapter
- occurred_at
- severity
- category
- summary
- environment
- evidence
- reproduce_steps
- diagnosis
- ai_task

### sosreport：诊断证据包

Doctor link 每次诊断都要生成标准证据包，而不是只打印一段日志。

标准目录：

```text
DoctorReports/
└── <timestamp>_<project>_<issue>/
    ├── summary.md
    ├── doctor-report.md
    ├── doctor-report.json
    ├── reproduce-steps.md
    ├── ai-task.md
    ├── fix-verification-checklist.md
    └── evidence/
        ├── environment.json
        ├── logs/
        ├── screenshots/
        ├── command-output/
        ├── test-results/
        └── attachments/
```

### OpenTelemetry：结构化采集

Doctor link 不需要实现完整观测平台，但需要采用结构化信号分层：

- logs
- metrics
- traces
- events
- environment
- artifacts

### Playwright Trace：复现路径

Doctor link 需要 timeline，用来记录问题发生过程。

示例字段：

- step
- action
- target
- timestamp
- result
- evidence

### Repomix：AI 上下文打包

Doctor link 必须输出 AI 可读上下文，让 Codex / AI Code 不靠猜。

必须输出：

- ai-task.md
- ai-context.json
- fix-verification-checklist.md

### OSV Scanner：扫描结果结构化

Doctor link 需要为每个诊断结果提供状态和风险等级：

- status: passed / failed / partial / unknown
- severity: info / warning / error / critical
- confidence: low / medium / high
- category
- next_action

## 2. 合并后的正式需求

### 2.1 统一诊断事件

Doctor link 必须支持统一的 Diagnostic Event 模型。事件类型至少包括：

- playback_failure
- network_failure
- build_failure
- runtime_error
- test_failure
- dependency_failure
- unknown_issue

### 2.2 标准证据包

每次诊断必须生成完整证据包，包含：

- 系统环境
- 项目环境
- 命令输出
- 日志
- 文件扫描结果
- 测试结果
- 截图
- 用户备注
- 外部工具输出

### 2.3 适配器机制

Doctor link 必须采用适配器架构。

第一批适配器：

- GenericAdapter
- VlyAdapter
- PythonAdapter
- NodeAdapter
- MacAppAdapter

### 2.4 AI 协作输出

Doctor link 生成的 AI 任务必须包含：

- 问题摘要
- 已有证据
- 复现步骤
- 失败阶段
- 修复边界
- 验证清单

### 2.5 Go / No-Go 评估

Doctor link 必须支持阶段性质量判断。例如 Vly Core Proof：

- Go：播放能力达到下一阶段门槛。
- No-Go：全能播放验证失败，暂停 UI / 媒体库开发。

判断必须来自测试数据。

## 3. Vly 场景强化需求

VlyAdapter 必须支持：

- 扫描测试样片库
- 识别封装格式
- 调用 ffprobe / MediaInfo
- 生成播放测试矩阵
- 记录手动或半自动播放结果
- 标记失败阶段
- 生成 Vly 专用诊断报告
- 生成 Codex 修复任务
- 生成 Vly Core Proof Go / No-Go 结论

Vly 第一阶段特别关注：

- 全格式播放
- 原盘播放
- 字幕
- 音轨
- 本地模拟 NAS
- 失败原因定位

## 4. 下一步开发优先级

1. 建立 DiagnosticEvent 数据模型。
2. 建立 DiagnosticPackage 输出结构。
3. 新增 environment_collector.py。
4. 新增 command_runner.py。
5. 新增 media_probe.py，调用 ffprobe。
6. 新增 test_recorder.py。
7. 强化 ai_task_generator.py。
8. 增加 doctor-report.schema.json。
9. 增加 Vly Core Proof 示例报告。
10. 增加 GitHub Issue / Codex task 输出模板。

## 5. 设计原则

- 证据优先。
- 结果可复现。
- 报告可读。
- JSON 可机器处理。
- Markdown 可给人和 AI 阅读。
- 适配器可扩展。
- 不绑定 Vly。
- 为 AI 提供足够上下文。
- 修复后必须能验证。
