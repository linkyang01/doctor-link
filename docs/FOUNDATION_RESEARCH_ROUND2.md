# Doctor link 二次参考研究：按新定位重看地基

## 1. 本轮研究前提

Doctor link 的定位已经改变：

> Doctor link 不是日志工具，也不是普通 AI Prompt 生成器，而是人和 AI 共用的软件诊断协作层。

因此，本轮研究不再寻找“同款工具”，而是寻找能补强 Doctor link 地基的成熟能力。

## 2. 新参考方向

### 2.1 AI Coding Agent：OpenHands / Aider / Continue

这些工具代表 AI 编码与 AI 检查方向。

可吸收能力：

- AI 需要代码上下文；
- AI 需要明确任务；
- AI 需要检查规则；
- AI 需要测试和验证；
- AI 修改代码后应有可追踪结果。

对 Doctor link 的启发：

Doctor link 不应该做代码修改，而应该为这些 AI 工具提供更高质量的诊断输入。

Doctor link 需要输出：

- ai-task.md；
- ai-context.json；
- fix-verification-checklist.md；
- investigation-boundary.md；
- user-assertions.json。

Doctor link 的目标是让 AI Code 不再从模糊描述开始，而是从诊断包开始。

### 2.2 Session Replay：rrweb / OpenReplay / Highlight

这些工具强调用户操作回放、事件时间线和问题现场。

可吸收能力：

- 记录用户操作；
- 记录事件时间线；
- 重放问题现场；
- 关联日志、网络请求、错误事件；
- 帮助人理解问题发生过程。

对 Doctor link 的启发：

Doctor link 需要 Timeline 与 Reproduction，不只是日志。

对于桌面软件和 Vly 场景，可以先用半自动方式记录：

- 打开文件；
- 点击播放；
- 切换字幕；
- 切换音轨；
- 失败出现；
- 用户标注失败点。

后续再扩展为可视化 Human Diagnosis View。

### 2.3 Observability：OpenTelemetry / Logfire / Langfuse

这些项目强调结构化采集、事件追踪和 AI 运行可观测。

可吸收能力：

- 统一事件；
- 日志、指标、事件、追踪分层；
- 结构化上下文；
- 运行过程可回溯；
- LLM 调用和 AI 推理过程也可被观测。

对 Doctor link 的启发：

Doctor link 需要 Signals 模型：

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

### 2.4 Debug Protocol：debugpy / DAP 思路

这些工具强调调试器与 IDE 之间的协议化通信。

可吸收能力：

- 调试事件标准化；
- 断点、堆栈、变量、线程等结构化；
- 客户端和调试引擎解耦。

对 Doctor link 的启发：

Doctor link 未来也需要自己的诊断协议：

- diagnostic event；
- evidence item；
- timeline step；
- user assertion；
- AI task；
- verification result。

这个协议比具体界面更重要。

### 2.5 API / Manual Testing：Bruno 等工具

这类工具强调把测试请求、测试数据和结果保存为文件，便于版本管理。

可吸收能力：

- 测试用例文件化；
- 测试结果可保存；
- 适合 Git 版本管理；
- 人可以编辑测试用例。

对 Doctor link 的启发：

Doctor link 的测试矩阵、用户断言、验证清单都应该文件化。

比如：

```text
.doctorlink/
├── doctorlink.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

### 2.6 Crash / Symbolication：Sentry symbolic 等

这类工具强调崩溃栈、符号化和错误归因。

可吸收能力：

- 崩溃信息解析；
- 堆栈符号化；
- 错误定位；
- 版本关联。

对 Doctor link 的启发：

对于 macOS / iOS 项目，Doctor link 未来需要支持：

- crash log 收集；
- 崩溃报告归档；
- App 版本关联；
- 符号文件路径记录；
- 崩溃栈作为证据。

## 3. 本轮研究后的地基调整

Doctor link 应从“报告生成工具”调整为五层架构：

```text
Layer 1: Diagnostic Protocol
Layer 2: Evidence Collection
Layer 3: Human Diagnosis Surface
Layer 4: AI Collaboration Package
Layer 5: Fix Verification Loop
```

### Layer 1: Diagnostic Protocol

定义核心数据结构：

- DiagnosticEvent；
- EvidenceItem；
- TimelineStep；
- UserAssertion；
- ProblemMap；
- AITask；
- VerificationChecklist。

### Layer 2: Evidence Collection

采集证据：

- 环境；
- 日志；
- 命令输出；
- 文件信息；
- 测试结果；
- 截图；
- 外部工具输出。

### Layer 3: Human Diagnosis Surface

给人看的诊断层：

- summary.md；
- problem-map.md；
- timeline.md；
- evidence-list.md；
- user-assertions.json。

### Layer 4: AI Collaboration Package

给 AI / Codex 的任务层：

- ai-context.json；
- ai-task.md；
- investigation-boundary.md；
- code-change-scope.md。

### Layer 5: Fix Verification Loop

修复验证闭环：

- fix-verification-checklist.md；
- before-report.json；
- after-report.json；
- regression-result.json；
- Go / No-Go 结论。

## 4. 需要立即落地的地基文件

### 4.1 配置文件

```text
.doctorlink/doctorlink.yml
.doctorlink/test-matrix.yml
.doctorlink/assertions.yml
.doctorlink/verification.yml
```

### 4.2 核心模型

```text
doctor_link/core/models.py
```

需要新增：

- DiagnosticEvent；
- EvidenceItem；
- TimelineStep；
- UserAssertion；
- ProblemMap；
- AITask；
- VerificationChecklist；
- DiagnosticPackage。

### 4.3 输出生成器

```text
doctor_link/core/package_builder.py
doctor_link/core/problem_map_builder.py
doctor_link/core/user_assertion_manager.py
doctor_link/core/verification_builder.py
```

### 4.4 AI 协作模板

```text
doctor_link/templates/ai-task.md.j2
doctor_link/templates/problem-map.md.j2
doctor_link/templates/fix-verification-checklist.md.j2
```

## 5. 新增关键产品原则

1. 先协议，后界面。
2. 先证据结构，后 AI 任务。
3. 用户确认问题优先级高于 AI 猜测。
4. AI 不得无证据忽略用户确认的问题。
5. 每次修复必须有前后对比。
6. 测试和断言必须文件化，便于版本管理。
7. Doctor link 不修代码，只让 AI 修得更准。

## 6. 对 Vly 的影响

Vly 的全能播放验证不能只是“播放几个文件看看”。

必须形成：

- Vly test matrix；
- Vly playback evidence；
- Vly user assertion；
- Vly AI repair task；
- Vly fix verification report。

也就是说，Vly 是 Doctor link 验证工具能力的第一个真实复杂场景。
