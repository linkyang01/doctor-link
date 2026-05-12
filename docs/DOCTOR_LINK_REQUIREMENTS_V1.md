# Doctor link 需求整理 V1

## 1. 新认识

Doctor link 不是普通日志工具，也不是单纯给 AI 看的报告生成器。

Doctor link 的定位应升级为：

> 面向 AI Code / Codex / 非程序员用户的软件诊断协作工具。

它要解决的问题不是“AI 不会写代码”，而是“AI 缺少问题现场、证据、复现路径、用户判断和修复验证标准”。

Doctor link 的核心价值是：

1. 把模糊问题变成结构化诊断包；
2. 把用户观察变成 AI 可执行任务；
3. 把日志、环境、时间线、测试结果和人工判断整合起来；
4. 在 AI 找不到问题、误判问题、忽略问题时，让用户可以明确指出问题；
5. 修复后用同一套测试与证据验证是否真的解决。

## 2. 核心定位

Doctor link 是一个独立工具，不绑定 Vly。

Vly 只是 Doctor link 的第一个真实应用场景。

Doctor link 长期应成为：

- AI 编程工具的诊断上下文层；
- 非程序员用户的问题表达工具；
- 人和 AI 共同使用的诊断工作台；
- 可复用到多个软件项目的通用诊断框架。

## 3. 目标用户

### 3.1 AI / Codex / AI Code

AI 需要读取：

- 结构化 JSON；
- 诊断报告；
- 复现步骤；
- 证据目录；
- AI 修复任务；
- 修复验证清单；
- 用户确认问题；
- 调查边界。

### 3.2 人类用户

人类用户需要看到：

- 问题摘要；
- 问题发生在哪里；
- 哪一步失败；
- 哪些证据重要；
- AI 可能忽略了什么；
- 哪些原因已经排除；
- 下一步应该让 AI 查什么；
- 如何明确标记“这里就是问题”。

### 3.3 项目维护者

项目维护者需要：

- 统一问题报告格式；
- 统一测试矩阵；
- 修复前后报告对比；
- Go / No-Go 阶段判断；
- 回归测试依据。

## 4. Doctor link 解决的核心问题

### 4.1 AI 找 Bug 难的原因

AI 在大项目里找 Bug 变难，不是因为不会写代码，而是缺少以下信息：

1. 运行环境；
2. 精确复现步骤；
3. 失败前后的日志；
4. 用户操作时间线；
5. 输入文件或测试数据；
6. 外部工具输出；
7. 版本与依赖状态；
8. 构建和测试历史；
9. 之前失败的修复尝试；
10. 修复后的验收标准；
11. 用户主观确认的问题点。

没有这些信息，AI 容易：

- 猜测根因；
- 修改错误模块；
- 大范围重构；
- 忽略真正问题；
- 修复表面现象；
- 引入新问题；
- 无法证明修复有效。

### 4.2 Doctor link 的补位

Doctor link 不替代 Codex，也不直接竞争 AI Code。

Doctor link 补足的是：

> 问题现场 → 结构化诊断 → 人工确认 → AI 任务 → 修复验证

它是 AI 编码前的诊断输入层，也是 AI 修改后的验证输出层。

## 5. 产品形态

Doctor link 应长期保持独立。

推荐阶段：

1. CLI 工具；
2. 本地 Web UI；
3. 项目适配器体系；
4. AI / Codex 协作连接器；
5. 可复用诊断框架。

第一阶段不追求复杂界面，但必须保证诊断包结构正确。

## 6. 核心能力模块

### 6.1 Evidence Collector 证据采集器

负责采集：

- 系统信息；
- 项目信息；
- 应用版本；
- 依赖版本；
- 日志文件；
- 命令输出；
- 测试数据；
- 截图或附件；
- 外部工具输出；
- 用户备注。

### 6.2 Reproduction Recorder 复现记录器

负责记录：

- 操作步骤；
- 时间线；
- 用户动作；
- 失败节点；
- 期望结果；
- 实际结果。

### 6.3 Failure Classifier 失败分类器

初始分类包括：

- playback_failure；
- network_failure；
- build_failure；
- runtime_error；
- test_failure；
- dependency_failure；
- permission_failure；
- configuration_failure；
- unknown_issue。

### 6.4 Human Diagnosis View 人类诊断视图

用于让人看懂问题。

应展示：

- 问题摘要；
- 失败阶段；
- 时间线；
- 证据列表；
- 可能原因排序；
- 已排除原因；
- 建议检查模块；
- 下一步行动；
- 可重新生成的 AI 任务。

### 6.5 User Assertion 用户确认问题

这是 Doctor link 的关键能力。

当 AI 没发现问题，或者 AI 不认为这是问题时，用户可以明确标记：

- 这里就是问题；
- 这个行为不符合预期；
- 这个结果不能接受；
- 这个日志很重要；
- 这个步骤就是失败点；
- AI 当前判断是错的；
- 不要忽略这个线索；
- 不要继续修改无关模块。

用户确认问题必须作为一等诊断信号进入报告和 AI 任务。

### 6.6 Human Override 人工覆盖机制

用户可以覆盖 AI 的判断：

- 标记 AI 诊断不完整；
- 标记 AI 诊断错误；
- 标记证据重要；
- 标记失败阶段；
- 锁定调查范围；
- 排除错误方向；
- 重新生成聚焦后的 AI 任务。

### 6.7 AI Context Packager AI 上下文打包器

输出 AI 可读上下文：

- ai-context.json；
- ai-task.md；
- doctor-report.md；
- reproduce-steps.md；
- fix-verification-checklist.md。

要求：AI 任务必须基于证据，不允许无证据猜测。

### 6.8 Fix Verifier 修复验证器

修复后必须验证：

- 原问题是否复现；
- 失败样本是否通过；
- 修复前后报告是否变化；
- 回归测试是否通过；
- 用户确认问题是否解决。

## 7. 标准诊断包

每次诊断必须生成标准目录：

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

## 8. 核心数据模型

### 8.1 DiagnosticEvent

描述一次诊断事件。

字段建议：

- event_id；
- project；
- adapter；
- occurred_at；
- severity；
- category；
- summary；
- environment；
- timeline；
- evidence；
- reproduce_steps；
- diagnosis；
- user_assertions；
- ai_task；
- verification_checklist。

### 8.2 UserAssertion

描述用户确认的问题。

字段建议：

- assertion_id；
- report_id；
- created_at；
- severity；
- user_statement；
- related_step；
- related_evidence；
- related_file；
- expected_behavior；
- actual_behavior；
- why_user_thinks_it_is_wrong；
- ai_disagreed_or_missed；
- investigation_scope；
- locked_scope；
- next_ai_instruction。

### 8.3 ProblemMap

描述问题地图。

字段建议：

- user_symptom；
- failure_stage；
- evidence；
- possible_root_causes；
- ruled_out_causes；
- related_modules；
- next_action；
- human_confirmed_problem。

## 9. AI 任务生成原则

Doctor link 生成的 AI 任务必须包含：

1. 问题摘要；
2. 用户确认问题；
3. 现有证据；
4. 复现步骤；
5. 失败阶段；
6. 已排除方向；
7. 调查范围；
8. 禁止修改范围；
9. 修复目标；
10. 修复后验证清单。

其中必须明确：

> The human user has confirmed this as the problem. Do not dismiss it as normal behavior without evidence.

中文含义：

> 用户已确认这是问题。不要在没有证据的情况下把它判断为正常行为。

## 10. 适配器架构

Doctor link 必须支持项目适配器。

第一批适配器：

- GenericAdapter；
- VlyAdapter；
- PythonAdapter；
- NodeAdapter；
- MacAppAdapter。

适配器职责：

- 定义采集内容；
- 定义测试命令；
- 定义日志路径；
- 定义证据类型；
- 定义 AI 任务模板；
- 定义修复验证清单。

## 11. doctorlink.yml

每个项目可以配置一个 `doctorlink.yml`，声明如何被诊断。

示例：

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

## 12. Vly 首个场景

Vly 是 Doctor link 的第一个应用场景。

Vly 中 Doctor link 需要验证：

- 全格式播放；
- 原盘播放；
- 字幕；
- 音轨；
- 本地模拟 NAS；
- 播放失败定位；
- 用户确认问题；
- Go / No-Go 结论。

特别注意：如果用户确认“播放不完整”，即使播放器没有崩溃，也必须视为问题。例如：

- 有画面但无声音；
- 有声音但字幕不显示；
- 能播放但音轨不对；
- 媒体识别成功但播放失败；
- AI 判断成功但用户确认体验失败。

## 13. 阶段规划

### Phase 1：诊断基础

- DiagnosticEvent；
- DiagnosticPackage；
- 标准报告目录；
- environment_collector；
- command_runner；
- doctor-report schema。

### Phase 2：证据采集

- 系统信息；
- 项目信息；
- 日志；
- 命令输出；
- 附件占位；
- 证据目录。

### Phase 3：人类诊断与标注

- Human Diagnosis View；
- Problem Map；
- User Assertion；
- Human Override；
- 重新生成聚焦 AI 任务。

### Phase 4：AI 协作

- ai-context.json；
- ai-task.md；
- reproduce-steps.md；
- fix-verification-checklist.md；
- Codex-ready task；
- GitHub Issue template。

### Phase 5：Vly Adapter

- media_probe；
- playback test matrix；
- Vly Core Proof report；
- test_recorder；
- Go / No-Go evaluator。

## 14. 成功标准

Doctor link 真正有用的标准：

1. 能把一句模糊问题转成结构化诊断包；
2. 能让 AI 明确知道该查什么；
3. 能让用户明确指出 AI 忽略的问题；
4. 能保留用户确认的问题作为一等信号；
5. 能生成可执行的 AI 修复任务；
6. 能生成修复验证清单；
7. 能对比修复前后结果；
8. 能在 Vly 这种复杂项目里减少 AI 盲改。
