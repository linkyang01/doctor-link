# Doctor link 项目目标与地基框架

## 1. 项目最终目标

Doctor link 是一个面向 AI Code / Codex / 非程序员用户的软件问题自动解决工具。

它的目标不是替代 AI 编码模型，也不是做普通日志查看器，而是把诊断、AI 修复和独立验证编排成一条可以直接运行的闭环：

> 描述问题 → 自动复现 → Codex 修复 → 独立重测 → 交付证据。

Doctor link 仍以诊断上下文层为地基，但不能停在“生成诊断包”。它要把“模糊问题”转化为可执行命令和结构化证据，在用户明确授权后创建隔离修复分支、调用 Codex 修改代码、最多迭代三轮，并用独立于 Codex 自述的复现和回归命令判断是否真的修好。

## 2. 一句话定位

> Doctor link 是人和 AI 共用的软件问题解决编排层：它复现问题、约束 Codex 修复、独立验收结果，并保留可审计和可回滚的完整证据。

## 3. 不做什么

Doctor link 不做以下事情：

1. 不替代 Codex / Aider / OpenHands / Continue 等 AI 编码工具；
2. 不自行充当代码生成模型，而是在用户授权后安全调用 Codex 完成修复；
3. 不做普通日志查看器；
4. 不做传统监控平台；
5. 不绑定 Vly；
6. 不依赖嵌入 SDK 才能工作。

## 4. 要做什么

Doctor link 要做以下事情：

1. 收集运行环境、日志、命令输出、测试结果、文件信息和截图附件；
2. 记录用户操作时间线和复现步骤；
3. 生成问题地图，展示失败阶段、证据、可能原因和已排除原因；
4. 支持用户明确标记“这里就是问题”；
5. 允许用户覆盖 AI 的错误判断；
6. 生成 AI / Codex 可执行的修复任务；
7. 生成修复验证清单；
8. 对比修复前后的诊断报告；
9. 支持项目级诊断规则文件化；
10. 通过适配器扩展到不同项目类型。
11. 提供一条 `doctor-link solve` 自动解决入口；
12. 在修复前要求干净 Git 工作区并创建独立修复分支；
13. 保存每轮 AI 输入、事件、错误和独立验证回执；
14. 只有全部必选复现与回归命令通过，才输出 `verified`。

## 4.1 当前可交付的自动解决纵切面

当前可交付纵切面明确支持 Python 与 Node.js JavaScript/TypeScript 项目，仍不笼统宣称“支持所有语言”，以确保每种项目都能可靠复现和验收：

```bash
# 先复现并生成修复预演，不修改代码
doctor-link solve /path/to/python-project \
  --problem "提交订单后产生两次扣款" \
  --test-command "python -m pytest tests/test_checkout.py -q"

# 审查预演后明确授权，才创建分支并调用 Codex
doctor-link solve /path/to/python-project \
  --problem "提交订单后产生两次扣款" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --allow-repair
```

Node.js 项目可显式提供命令，也可让 Doctor link 根据 `packageManager`、锁文件和 `scripts.test` 选择 npm、pnpm、Yarn 或 Bun；没有可用测试脚本但存在 JavaScript 测试文件时，可回退到 `node --test`：

```bash
doctor-link solve /path/to/node-project \
  --problem "并发更新时丢失最后一次写入" \
  --test-command "npm test" \
  --allow-repair
```

如果项目已经配置 `.doctorlink/reproduce.yml` 和 `.doctorlink/test-matrix.yml`，可省略命令参数。Doctor link 会执行配置中的复现和测试命令；全部命令已经通过时返回 `not_reproduced`，不会允许 AI 无目标改代码。混合语言单体仓库应从目标包目录运行，并优先显式提供命令，避免仓库级自动发现产生歧义。

## 5. 核心设计原则

### 5.1 证据优先

所有诊断结论必须关联证据。

没有证据的推断只能作为假设，不能作为结论。

### 5.2 复现优先

一个问题如果不能复现，就很难被 AI 正确修复。

Doctor link 必须尽量记录：

- 操作步骤；
- 失败步骤；
- 输入数据；
- 环境信息；
- 关联日志；
- 期望结果；
- 实际结果。

### 5.3 用户确认问题优先

用户确认的问题必须作为一等诊断信号。

当 AI 认为“正常”，但用户确认“这就是问题”时，Doctor link 必须记录该判断，并在 AI 任务中明确要求 AI 不得无证据忽略。

### 5.4 先协议，后界面

Doctor link 的地基不是 UI，而是诊断协议。

先把数据结构、报告结构、证据结构和 AI 任务结构定义稳定，再做 CLI、Web UI 或桌面 UI。

### 5.5 修复必须验证

AI 不能只说“已修复”。

每次修复后，Doctor link 必须提供验证清单，并支持修复前后报告对比。

### 5.6 规则文件化

诊断规则、测试矩阵、用户断言、验证规则必须可以进入仓库。

建议目录：

```text
.doctorlink/
├── doctorlink.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

## 6. 五层地基架构

Doctor link 采用五层架构。

```text
Layer 1: Diagnostic Protocol
Layer 2: Evidence Collection
Layer 3: Human Diagnosis Surface
Layer 4: AI Collaboration Package
Layer 5: Authorized Repair and Verification Loop
```

### 6.1 Layer 1：Diagnostic Protocol 诊断协议层

定义 Doctor link 的核心数据结构，是整个项目最重要的地基。

核心模型：

- DiagnosticEvent：一次问题事件；
- DiagnosticPackage：一次诊断包；
- EvidenceItem：一条证据；
- TimelineStep：一个操作或事件步骤；
- UserAssertion：用户确认的问题；
- ProblemMap：问题地图；
- AITask：AI 修复任务；
- VerificationChecklist：修复验证清单。

### 6.2 Layer 2：Evidence Collection 证据采集层

负责采集和归档证据。

证据类型：

- environment：系统与运行环境；
- logs：日志；
- commands：命令输出；
- events：事件；
- timeline：时间线；
- user_assertions：用户确认问题；
- test_results：测试结果；
- artifacts：截图、附件、样片信息等。

### 6.3 Layer 3：Human Diagnosis Surface 人类诊断层

负责让用户看懂问题、指出问题、纠正 AI。

输出内容：

- summary.md：非技术摘要；
- problem-map.md：问题地图；
- timeline.md：时间线；
- evidence-list.md：证据列表；
- user-assertions.json：用户确认问题。

### 6.4 Layer 4：AI Collaboration Package AI 协作层

负责把诊断结果变成 AI 可执行任务。

输出内容：

- ai-context.json：AI 上下文；
- ai-task.md：AI 修复任务；
- investigation-boundary.md：调查边界；
- fix-verification-checklist.md：修复验证清单。

AI 任务必须包含：

1. 问题摘要；
2. 用户确认问题；
3. 已有证据；
4. 复现步骤；
5. 失败阶段；
6. 已排除方向；
7. 调查范围；
8. 禁止修改范围；
9. 修复目标；
10. 修复后验证清单。

### 6.5 Layer 5：Authorized Repair and Verification Loop 授权修复与验证闭环

负责在用户明确授权后创建隔离分支、调用 AI 修复，并判断 AI 是否真的修好了问题。AI 返回成功、写入补丁或退出码为 0，都不能替代 Doctor link 的独立重测。

输出内容：

- solve-session.json；
- solve-summary.md；
- round-N/prompt.md；
- round-N/codex-events.jsonl；
- round-N/verification.json；
- verified / failed / blocked 结论。

## 7. 标准诊断包结构

每次诊断都生成一个标准包：

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

## 8. 核心运行模式

Doctor link 支持三种诊断模式。

### 8.1 External Mode 外部诊断模式

Doctor link 不进入目标程序内部，只在外部收集信息。

能力：

- 扫描项目文件；
- 收集环境信息；
- 收集日志；
- 执行配置命令；
- 生成诊断包；
- 接受用户确认问题；
- 生成 AI 任务和验证清单。

这是第一版必须优先实现的模式。

### 8.2 Sidecar Mode 伴随运行模式

Doctor link 与目标程序同时运行，像旁路观察员。

能力：

- 监听日志文件；
- 观察进程状态；
- 记录文件变化；
- 记录测试执行；
- 允许用户手动标记失败点。

### 8.3 Embedded SDK Mode 嵌入式 SDK 模式

目标程序可选接入轻量 SDK，主动上报内部事件。

能力：

- 上报内部生命周期；
- 上报业务事件；
- 上报失败阶段；
- 提供更精确的运行时诊断。

该模式是可选增强，不是使用 Doctor link 的前提。

## 9. 诊断状态流转

参考成熟事故响应与复盘流程，Doctor link 诊断包应有状态。

状态建议：

- Draft：信息收集中；
- In Review：等待用户或 AI 复核；
- AI Ready：可以交给 AI 修复；
- Fixing：正在修复；
- Verifying：正在验证；
- Closed：问题关闭；
- Reopened：问题复现。

## 10. 用户确认问题机制

### 10.1 UserAssertion

用户可以明确标记：

- 这里就是问题；
- 这个现象不符合预期；
- AI 判断正常但我确认异常；
- 这个证据很重要；
- 这个步骤就是失败点；
- 这个方向不要再查；
- 这个模块不要乱改。

### 10.2 Human Override

用户可以覆盖 AI 判断：

- AI 诊断不完整；
- AI 诊断错误；
- AI 忽略了关键现象；
- AI 改错了模块；
- AI 没有验证。

### 10.3 AI 任务中必须明确

当存在用户确认问题时，ai-task.md 必须写入：

> The human user has confirmed this as the problem. Do not dismiss it as normal behavior without evidence.

中文含义：

> 用户已确认这是问题。不要在没有证据的情况下把它判断为正常行为。

## 11. 项目配置协议

每个项目可用 `.doctorlink/` 定义诊断方式。

### 11.1 doctorlink.yml

定义项目、采集项、日志、命令、适配器。

### 11.2 test-matrix.yml

定义测试矩阵。

### 11.3 assertions.yml

定义用户确认问题和项目特有验收规则。

### 11.4 verification.yml

定义修复后的验证清单。

## 12. Vly 作为首个应用场景

Vly 是 Doctor link 的第一个真实复杂场景。

Vly 场景中 Doctor link 要验证：

- 全格式播放；
- 原盘播放；
- 字幕；
- 音轨；
- 本地模拟 NAS；
- 播放失败定位；
- 用户确认问题；
- Go / No-Go 结论。

Vly 中典型用户确认问题：

- 有画面但无声音，不能算播放成功；
- 有声音但字幕不显示，不能算播放成功；
- 能打开但音轨不对，不能算播放成功；
- AI 判断正常但用户确认体验失败；
- 播放不完整就是失败。

## 13. P0 落地任务

### 13.1 数据模型

- DiagnosticEvent；
- DiagnosticPackage；
- EvidenceItem；
- TimelineStep；
- UserAssertion；
- ProblemMap；
- AITask；
- VerificationChecklist。

### 13.2 目录与输出

- 标准诊断包目录生成；
- summary.md；
- problem-map.md；
- timeline.md；
- evidence-list.md；
- doctor-report.json；
- ai-context.json；
- ai-task.md；
- fix-verification-checklist.md；
- user-assertions.json。

### 13.3 命令

```bash
doctor-link init
doctor-link scan
doctor-link report
doctor-link assert
doctor-link ai-task
doctor-link verify-plan
```

### 13.4 配置模板

- .doctorlink/doctorlink.yml；
- .doctorlink/test-matrix.yml；
- .doctorlink/assertions.yml；
- .doctorlink/verification.yml。

## 14. P1 落地任务

- environment_collector.py；
- command_runner.py；
- log_collector.py；
- media_probe.py；
- test_recorder.py；
- problem_map_builder.py；
- user_assertion_manager.py；
- verification_builder.py；
- package_builder.py。

## 15. 第一版成功标准

Doctor link 第一版不是“命令能跑”就算成功。

必须完成一次完整闭环：

1. 用户输入或选择一个问题；
2. Doctor link 生成标准诊断包；
3. 用户能标记“这里就是问题”；
4. Doctor link 生成问题地图；
5. Doctor link 生成 AI 修复任务；
6. AI 有明确证据和修改边界；
7. Doctor link 生成修复验证清单；
8. 修复后能对比前后报告。

## 16. 最终目标

Doctor link 要成为 AI Coding 工具的诊断上下文层。

它的最终价值是：

- 让 AI 少猜；
- 让用户能指出问题；
- 让证据能追溯；
- 让修复有边界；
- 让结果能验证；
- 让复杂项目中的 AI Debugging 更可靠。
