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
- 修复前后诊断报告对比；
- 诊断包打包交付；
- 本地诊断包浏览。

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
doctor-link record <package_dir> --name "测试名称" --status partial
doctor-link vly-proof <library> --package-dir <package_dir>
doctor-link compare before.json after.json --package-dir <package_dir>
doctor-link doctor-package <package_dir> --out DoctorReports/package.zip
doctor-link view <package_dir>
```

## 一键证据采集

`doctor-link collect` 用于把环境、日志、命令输出、媒体探测和附件统一采集到已有诊断包中。

示例：

```bash
doctor-link collect DoctorReports/<package_dir> \
  --project-root . \
  --logs "logs/*.log" \
  --command "python --version" \
  --probe sample.mp4 \
  --attachment input.txt \
  --note "用户复现问题后的补充证据"
```

采集后会更新：

- `doctor-report.json`
- `evidence-list.md`
- `timeline.md`
- `summary.md`
- `ai-task.md`
- `evidence/environment.json`
- `evidence/logs/`
- `evidence/command-output/`
- `evidence/test-results/`
- `evidence/attachments/`

即使命令执行失败或媒体 probe 失败，失败结果也会作为证据保留，而不是被静默忽略。

### 敏感信息过滤

`doctor-link collect` 默认会对日志和命令输出进行敏感信息过滤，并生成：

- `redaction-report.md`
- `redaction-report.json`

默认过滤内容包括：

- password
- secret
- api_key / api-key
- access_token / access-token
- token
- Cookie
- Authorization Header

可选增强过滤：

```bash
doctor-link collect DoctorReports/<package_dir> \
  --logs "logs/*.log" \
  --redact-email \
  --redact-phone \
  --redact-pattern "internal-[0-9]+"
```

如确需保留原始日志和命令输出，可使用：

```bash
doctor-link collect DoctorReports/<package_dir> --logs "logs/*.log" --no-redact
```

使用 `--no-redact` 前应确认诊断包不会被外发，避免泄露 token、密码、Cookie 等敏感信息。

## 修复验证任务生成

`doctor-link verify` 用于读取诊断包中的验证清单、测试记录、用户确认问题、Vly proof 和 report comparison，生成验证计划与结构化验证结果。

示例：

```bash
doctor-link verify DoctorReports/<package_dir> --write-back
```

命令会生成：

- `verification-plan.md`
- `verification-result.json`

并在使用 `--write-back` 时更新：

- `doctor-report.json`
- `summary.md`
- `ai-task.md`

验证状态包括：

- `ready`
- `missing_evidence`
- `not_verified`
- `candidate_verified`
- `needs_review`

Doctor link 不会只因为生成了验证计划就宣称“已修复”，而是会列出缺失证据、需要重跑的测试和建议的下一步命令。

## 诊断包打包交付

`doctor-link doctor-package` 用于把标准诊断包导出为 zip，便于交付给 AI Code、Codex、开发人员或评审人员。

示例：

```bash
doctor-link doctor-package DoctorReports/<package_dir> \
  --out DoctorReports/doctor-package.zip
```

可选过滤：

```bash
doctor-link doctor-package DoctorReports/<package_dir> \
  --out DoctorReports/doctor-package.zip \
  --exclude-attachments \
  --exclude-logs \
  --exclude-screenshots \
  --max-file-size 1000000
```

导出时会生成：

- `manifest.json`：记录导出时间、校验结果、包含文件和跳过文件；
- `package-readme.md`：说明该 zip 的用途、校验结果和跳过文件；
- `.zip` 文件：保留原诊断包目录结构。

如果诊断包缺少必需文件，命令不会伪装成功，而是会在 manifest 和命令输出中保留警告。若诊断包不存在 `redaction-report.md`，导出说明中会提示需要人工复核敏感信息。

## 本地诊断包浏览器

`doctor-link view` 用于在本地浏览器中打开诊断包，只读查看诊断上下文，不修改诊断包内容。

示例：

```bash
doctor-link view DoctorReports/<package_dir>
```

可选参数：

```bash
doctor-link view DoctorReports/<package_dir> \
  --host 127.0.0.1 \
  --port 8765 \
  --no-open-browser
```

仅生成静态 HTML，不启动服务：

```bash
doctor-link view DoctorReports/<package_dir> --build-only
```

该命令会生成：

```text
DoctorReports/<package_dir>/.doctorlink-web/index.html
```

当前浏览内容包括：

- summary
- problem-map
- timeline
- evidence-list
- user-assertions
- ai-task
- investigation-boundary
- verification checklist / verification plan / verification result
- redaction report
- manifest
- package readme
- evidence 文件清单

P2 第一批 Web UI 只负责本地只读浏览，不做云端同步、不做账号登录、不替代 CLI 诊断流程。

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

`collect`、`verify`、`doctor-package` 会自动向上查找 `.doctorlink` 目录并读取默认配置。命令行显式参数优先级高于配置文件。

### collect.yml 示例

```yaml
collect:
  project_root: .
  logs:
    - logs/*.log
  commands:
    - python --version
    - doctor-link --help
  probes: []
  attachments: []
  redaction:
    enabled: true
    email: false
    phone: false
    patterns: []
```

### package.yml 示例

```yaml
package:
  output_dir: DoctorReports
  exclude_attachments: false
  exclude_logs: false
  exclude_screenshots: false
  max_file_size: 1000000
```

### verification.yml 示例

```yaml
verification:
  write_back: false
  required_signals:
    - test_records
    - report_comparison
```

如果没有手动传 `--logs`、`--command`、`--max-file-size` 等参数，Doctor link 会使用 `.doctorlink` 中的默认值；如果命令行提供了参数，则以命令行为准。

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

## 当前状态

Doctor link 当前已完成 P0/P1/P1+ 诊断地基，并进入 P2 本地 Web UI / 诊断包浏览器阶段。

已具备：

1. 核心数据模型；
2. 标准诊断包生成；
3. 用户确认问题支持；
4. 问题地图生成；
5. AI 任务生成；
6. 修复验证清单生成；
7. 证据采集基础命令；
8. 一键证据采集；
9. 敏感信息过滤；
10. 配置驱动采集、验证与打包；
11. 验证任务生成；
12. Vly proof；
13. 修复前后报告对比；
14. 诊断包 zip 导出；
15. 本地只读诊断包浏览器。

## 第一版成功标准

第一版真正成功，不是命令能跑，而是能完成以下闭环：

1. 用户报告或选择一个问题；
2. Doctor link 创建标准诊断包；
3. Doctor link 采集运行环境、日志、命令输出、媒体探测和附件；
4. Doctor link 对日志和命令输出进行敏感信息过滤；
5. 用户标记确认的问题；
6. Doctor link 生成问题地图；
7. Doctor link 生成 AI 可执行的修复任务；
8. AI 任务包含证据、边界和验证步骤；
9. Doctor link 生成修复验证计划；
10. 修复前后诊断报告可以对比；
11. 诊断包可以打包交付；
12. 诊断包可以本地可视化浏览。
