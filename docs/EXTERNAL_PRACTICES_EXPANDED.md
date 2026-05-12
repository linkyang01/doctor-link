# Doctor link 外部经验扩大研究

## 1. 研究目的

Doctor link 的定位已经从“诊断报告生成器”升级为“人和 AI 共用的软件诊断协作层”。因此，外部经验不再只看错误追踪工具，而要扩大到：

- 事故响应；
- 事后复盘；
- 用户行为回放；
- AI 编码工具；
- AI 检查；
- 可观测性；
- 调试协议；
- 测试用例文件化；
- 诊断证据包；
- 人工确认与协作流程。

目标是把这些成熟方法转化为 Doctor link 的可落地需求。

## 2. 事故响应与复盘经验

参考：PagerDuty Incident Response Documentation。

该文档强调事故处理不仅是解决当前问题，还包括事后复盘、责任人、时间线、日志、影响分析、原因分析和后续行动。

Doctor link 应吸收以下能力：

### 2.1 诊断所有权

每个诊断包应有明确状态和负责人。

建议字段：

- owner；
- status；
- created_at；
- updated_at；
- reviewer；
- follow_up_actions。

### 2.2 状态流转

Doctor link 诊断包应有状态：

- Draft：诊断信息还在收集；
- In Review：等待人或 AI 复核；
- AI Ready：可以交给 AI Code；
- Fixing：正在修复；
- Verifying：正在验证；
- Closed：问题关闭；
- Reopened：问题复现。

### 2.3 时间线优先

复盘文档强调时间线是核心。Doctor link 也必须把 timeline 作为一等结构。

每个 timeline step 应包含：

- 时间；
- 操作；
- 结果；
- 证据；
- 用户备注；
- 是否为失败点。

### 2.4 行动项

每次诊断后应生成 follow-up actions：

- 修复任务；
- 测试补充；
- 日志增强；
- 文档更新；
- 回归测试；
- 监控或诊断能力补充。

## 3. 用户行为回放经验

参考方向：rrweb / OpenReplay / Highlight。

这些项目不是只记录错误，而是记录“用户做了什么”。Doctor link 应吸收“问题现场可重建”的思想。

### 3.1 Record and Replay 思想

Doctor link 对桌面软件可以先不做完整录屏或自动回放，但必须能记录操作过程。

Vly 场景示例：

- 打开文件；
- 选择样片；
- 点击播放；
- 切换字幕；
- 切换音轨；
- 观察失败；
- 用户标记失败点。

### 3.2 证据和操作绑定

每条证据都应该能绑定到某个步骤。

例如：

- step 3：点击播放；
- evidence：player-log.txt；
- result：failed；
- user assertion：有画面但无字幕，用户确认失败。

## 4. AI 编码工具经验

参考方向：OpenHands / Aider / Continue。

这些工具说明 AI 编码需要明确上下文、任务、检查规则和验证结果。

Doctor link 应吸收：

### 4.1 AI 任务必须源自证据

Doctor link 生成 ai-task.md 时，必须包含：

- 诊断摘要；
- 证据；
- 复现步骤；
- 用户确认问题；
- 调查边界；
- 禁止修改范围；
- 验证清单。

### 4.2 AI 检查规则文件化

类似 Continue 的检查思路，Doctor link 应支持项目内规则：

```text
.doctorlink/
├── doctorlink.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

### 4.3 代码修改前必须问四个问题

AI 修改代码前，Doctor link 必须回答：

1. 到底哪里失败？
2. 如何复现？
3. 有什么证据？
4. 修好以后怎么验证？

## 5. 可观测性经验

参考方向：OpenTelemetry / Logfire / Langfuse。

Doctor link 不需要做完整观测平台，但必须建立信号分层。

### 5.1 Signals 模型

```text
signals/
├── environment
├── logs
├── commands
├── events
├── timeline
├── user_assertions
├── test_results
└── artifacts
```

### 5.2 统一事件结构

不同来源的证据必须能归入统一事件。

例如：

- 播放器日志；
- ffprobe 输出；
- 用户备注；
- 测试结果；
- AI 结论；
- 人工覆盖结论。

## 6. 调试协议经验

参考方向：debugpy / DAP。

Doctor link 的关键不是某个 UI，而是协议。

### 6.1 诊断协议优先

先定义：

- DiagnosticEvent；
- EvidenceItem；
- TimelineStep；
- UserAssertion；
- ProblemMap；
- AITask；
- VerificationChecklist；
- DiagnosticPackage。

CLI、Web UI、桌面 UI 都基于这个协议扩展。

## 7. 测试工具经验

参考方向：Bruno、Playwright、各种文件化测试工具。

Doctor link 应把测试矩阵和验证清单文件化。

### 7.1 文件化测试矩阵

```yaml
name: Vly Core Proof
cases:
  - id: mkv_hevc_dts
    type: playback
    required: true
  - id: bdmv_main_movie
    type: disc_source
    required: true
  - id: pgs_subtitle
    type: subtitle
    required: true
```

### 7.2 文件化用户断言

```yaml
assertions:
  - id: subtitle_missing_is_failure
    statement: 有画面但字幕没有显示，不能视为播放成功
    severity: error
```

### 7.3 文件化验证规则

```yaml
verification:
  - rerun_failed_samples
  - compare_before_after_reports
  - confirm_user_assertions_resolved
```

## 8. 对 Doctor link 地基的最终要求

经过扩大研究，Doctor link 地基必须包含：

### 8.1 协议层

- DiagnosticEvent；
- DiagnosticPackage；
- EvidenceItem；
- TimelineStep；
- UserAssertion；
- ProblemMap；
- AITask；
- VerificationChecklist。

### 8.2 证据层

- environment；
- logs；
- command outputs；
- screenshots；
- attachments；
- test results；
- external tool outputs。

### 8.3 人类诊断层

- summary.md；
- problem-map.md；
- timeline.md；
- evidence-list.md；
- user-assertions.json。

### 8.4 AI 协作层

- ai-context.json；
- ai-task.md；
- investigation-boundary.md；
- fix-verification-checklist.md。

### 8.5 验证闭环

- before-report.json；
- after-report.json；
- regression-result.json；
- Go / No-Go。

## 9. 新增产品原则

1. 问题不是日志，问题是用户期望与实际结果不一致。
2. 用户确认的问题必须进入诊断结构。
3. AI 的判断可以被用户覆盖。
4. 时间线是诊断核心。
5. 证据必须能追溯来源。
6. AI 任务必须基于证据生成。
7. 修复必须有验证清单。
8. 诊断规则必须文件化。
9. 每个诊断包必须可交给人看，也可交给 AI 看。
10. Doctor link 不修代码，但让 AI 修得更准。

## 10. 下一步落地

优先开发：

1. 扩展数据模型；
2. 生成标准诊断包；
3. 支持 user assertion；
4. 支持 problem map；
5. 支持 verification checklist；
6. 支持 .doctorlink 配置目录；
7. 强化 ai-task 生成；
8. 用 Vly 场景验证整个闭环。
