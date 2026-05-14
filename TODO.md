# Doctor link TODO

本文件用于项目化跟踪 Doctor link 的当前工作。每完成一项，必须把对应任务从 `[ ]` 改为 `[x]`。

## P0：项目管理地基

- [x] 明确 Doctor link 项目目标
- [x] 明确五层地基架构
- [x] 建立中英文 README
- [x] 建立 GitHub Actions CI
- [x] 建立 TODO.md
- [x] 建立 ADR 决策记录目录
- [x] 建立 P0 Diagnostic Foundation Issue
- [x] 建立 issue 模板

## P0：诊断协议层

- [x] 扩展 DiagnosticEvent 数据模型
- [x] 扩展 DiagnosticPackage 数据模型
- [x] 新增 EvidenceItem 数据模型
- [x] 新增 TimelineStep 数据模型
- [x] 新增 UserAssertion 数据模型
- [x] 新增 ProblemMap 数据模型
- [x] 新增 AITask 数据模型
- [x] 新增 VerificationChecklist 数据模型

## P0：标准诊断包

- [x] 新增 package_builder.py
- [x] 生成标准 DoctorReports 目录
- [x] 生成 summary.md
- [x] 生成 problem-map.md
- [x] 生成 timeline.md
- [x] 生成 evidence-list.md
- [x] 生成 doctor-report.json
- [x] 生成 ai-context.json
- [x] 生成 user-assertions.json

## P0：用户确认问题机制

- [x] 新增 user_assertion_manager.py
- [x] 增加 doctor-link assert 命令
- [x] 支持用户声明 expected_behavior
- [x] 支持用户声明 actual_behavior
- [x] 支持用户声明 why_user_thinks_it_is_wrong
- [x] 让 ai-task.md 强制包含用户确认问题

## P0：问题地图与 AI 任务

- [x] 新增 problem_map_builder.py
- [x] 输出 problem-map.md
- [x] 升级 ai_task_generator.py
- [x] 增加 investigation-boundary.md
- [x] 新增 verification_builder.py
- [x] 输出 fix-verification-checklist.md

## P0：项目配置协议

- [x] 新增 .doctorlink/doctorlink.yml 模板
- [x] 新增 .doctorlink/test-matrix.yml 模板
- [x] 新增 .doctorlink/assertions.yml 模板
- [x] 新增 .doctorlink/verification.yml 模板

## P1：证据采集能力

- [x] 新增 environment_collector.py
- [x] 新增 command_runner.py
- [x] 新增 log_collector.py
- [x] 新增 media_probe.py
- [x] 新增 test_recorder.py
- [x] 增加 doctor-link env 命令
- [x] 增加 doctor-link probe 命令
- [x] 增加 doctor-link record 命令

## P1：Vly Adapter

- [x] 定义 Vly Core Proof 测试矩阵
- [x] 支持 VlyTestLibrary 扫描
- [x] 支持 ffprobe 读取媒体信息
- [x] 支持播放测试结果记录
- [x] 支持 Go / No-Go 评估
- [x] 增加 doctor-link vly-proof 命令
- [x] 支持 vly-proof 写入标准诊断包

## P1：修复验证闭环

- [x] 新增 report_comparator.py
- [x] 增加 doctor-link compare 命令
- [x] 支持 before/after doctor-report.json 对比
- [x] 输出 report-comparison.json
- [x] 输出 report-comparison.md
- [x] 支持 compare 写入 after 标准诊断包

## P1：质量保障

- [x] 增加 P1 证据采集基础测试
- [x] 增加 CLI P1 烟测
- [x] 增加 Vly Adapter 基础测试
- [x] 增加 Vly Proof 诊断包写入测试
- [x] 增加 Report Comparison 基础测试
- [x] 增加 compare CLI 烟测
- [x] 增加 Report Comparison 诊断包写入测试

## P1+：项目管理与架构准备

- [x] 新建 GitHub Issue：P1+ Evidence Collection Pipeline
- [x] 新增 ADR：P1+ CLI evidence pipeline
- [x] 明确 P1+ 三个核心命令边界：collect / verify / doctor-package
- [x] 确认 P1+ 不引入 Web UI
- [x] 确认 P1+ 不改变 P0/P1 已有诊断协议

## P1+：doctor-package 诊断包打包

- [x] 新增 package_exporter.py
- [x] 实现诊断包结构校验
- [x] 检查必需文件是否存在
- [x] 生成 manifest.json
- [x] 生成 package-readme.md
- [x] 支持导出 zip
- [x] 支持默认包含完整诊断包
- [x] 支持排除 attachments / logs / screenshots
- [x] 支持 max-file-size 跳过超限文件
- [x] 保留目录结构
- [x] 防止路径穿越
- [x] 增加 doctor-link doctor-package 命令
- [x] 增加 package exporter 测试
- [x] 增加 doctor-package CLI 烟测
- [x] 更新 README.zh-CN.md
- [x] 更新 README.en.md

## P1+：collect 一键证据采集

- [x] 新增 collector.py
- [x] 支持环境信息采集并写入诊断包
- [x] 支持日志目录采集并写入诊断包
- [x] 支持命令执行输出采集并写入诊断包
- [x] 支持媒体 probe 采集并写入诊断包
- [x] 支持附件复制并写入诊断包
- [x] 每类证据生成 evidence item
- [x] 每次采集生成 timeline step
- [x] 写回 doctor-report.json
- [x] 写回 evidence-list.md
- [x] 写回 timeline.md
- [x] 写回 summary.md
- [x] 写回 ai-task.md
- [x] 增加 doctor-link collect 命令
- [x] 增加 collector 测试
- [x] 增加 collect CLI 烟测
- [x] 更新 README.zh-CN.md
- [x] 更新 README.en.md

## P1+：verify 验证任务生成

- [x] 新增 verification_runner.py
- [x] 读取 fix-verification-checklist.md
- [x] 读取 doctor-report.json
- [x] 读取 user-assertions.json
- [x] 读取 test_records
- [x] 读取 report_comparison
- [x] 读取 vly_core_proof
- [x] 判断验证状态：ready / missing_evidence / not_verified / candidate_verified / needs_review
- [x] 生成 verification-plan.md
- [x] 生成 verification-result.json
- [x] 输出缺失证据清单
- [x] 输出必须重跑的测试
- [x] 输出建议下一步命令
- [x] 增加 doctor-link verify 命令
- [x] 支持 --write-back
- [x] 写回 doctor-report.json
- [x] 写回 summary.md
- [x] 写回 ai-task.md
- [x] 增加 verification_runner 测试
- [x] 增加 verify CLI 烟测
- [x] 更新 README.zh-CN.md
- [x] 更新 README.en.md

## P1+：敏感信息过滤

- [x] 新增 redactor.py
- [x] 支持 token / secret / password / api_key / access_token 过滤
- [x] 支持 Cookie 与 Authorization Header 过滤
- [x] 支持用户自定义正则
- [x] 支持邮箱和手机号可选脱敏
- [x] 支持 redaction-report.md 输出
- [x] collect 采集命令输出时自动过滤
- [x] collect 采集日志时自动过滤
- [x] doctor-package 打包前可选过滤报告
- [x] 增加 --no-redact 参数
- [x] 增加 redactor 测试
- [x] 增加 redactor CI 覆盖
- [x] 更新 README.zh-CN.md
- [x] 更新 README.en.md

## P1+：.doctorlink 配置协议增强

- [x] 新增 config_loader.py
- [x] 新增 .doctorlink/collect.yml
- [x] 新增 .doctorlink/package.yml
- [x] 扩展 .doctorlink/doctorlink.yml
- [x] 扩展 .doctorlink/verification.yml
- [x] 支持默认项目根目录、日志、命令、probe、附件、排除目录
- [x] 支持默认敏感信息过滤规则
- [x] 支持默认最大文件大小和打包输出目录
- [x] 支持 CLI 参数覆盖配置文件
- [x] 支持配置校验
- [x] collect 接入配置读取
- [x] doctor-package 接入配置读取
- [x] verify 接入配置读取
- [x] 增加 config_loader 测试
- [x] 增加配置驱动 CLI 烟测
- [x] 更新 README.zh-CN.md
- [x] 更新 README.en.md

## P2：本地 Web UI / 诊断包浏览器基础

- [x] 新建 GitHub Issue：P2 Local Web UI / Diagnostic Package Browser
- [x] 新增 ADR：Local Web UI Boundary
- [x] 新增 web package reader
- [x] 新增静态 HTML 渲染器
- [x] 支持读取 summary / timeline / evidence / assertions / ai-task / verification
- [x] 支持读取 redaction report / manifest / package readme
- [x] 新增 doctor-link view 命令
- [x] 支持 --host / --port / --no-open-browser
- [x] 保持本地只读浏览，不修改诊断包
- [x] 增加 package reader 测试
- [x] 增加 HTML renderer 测试
- [x] 增加 view CLI 烟测
- [x] 更新 README.zh-CN.md
- [x] 更新 README.en.md

## P2：诊断工作台路线图

- [x] 新增 ADR：P2 Diagnostic Workbench Roadmap
- [ ] 将 P2 Web UI 从单包静态页升级为本地诊断工作台
- [ ] 保持本地优先、只读优先、证据优先、用户确认问题优先
- [ ] 明确任何写回能力都必须另写 ADR 并显式操作
- [ ] 更新 Issue #15，纳入完整 P2 工作台计划

## P2：诊断包列表与导航

- [ ] 新增 reports_indexer.py，扫描 DoctorReports 目录
- [ ] 识别多个标准诊断包
- [ ] 提取每个诊断包的项目名、问题摘要、创建时间、更新时间
- [ ] 提取 evidence 数量、timeline 步骤数、user assertion 数量
- [ ] 提取 verification 状态、redaction 状态、package export 状态
- [ ] 生成诊断包列表页
- [ ] 支持从列表页进入单个诊断包详情
- [ ] 支持按 verification 状态筛选
- [ ] 支持按是否存在用户确认问题筛选
- [ ] 支持按是否存在 redaction warning 筛选
- [ ] 增加 reports indexer 测试
- [ ] 增加 reports list HTML 测试
- [ ] 增加 CLI smoke 覆盖

## P2：诊断包详情页增强

- [ ] 将单页浏览拆分为 Overview / Timeline / Evidence / Assertions / AI Task / Verification / Redaction / Manifest 视图
- [ ] Overview 显示诊断状态摘要
- [ ] Timeline 高亮失败步骤、未知步骤和关键证据
- [ ] Evidence 支持按类型分组：environment / logs / command-output / test-results / attachments
- [ ] Assertions 高亮用户确认问题，并显示 expected / actual / why
- [ ] AI Task 高亮调查边界、禁止忽略用户确认问题、验证要求
- [ ] Verification 显示 missing_evidence、tests_to_rerun、next_commands
- [ ] Redaction 显示替换数量、命中规则、未过滤风险提示
- [ ] Manifest 显示 included / skipped 文件和导出校验结果
- [ ] 增加详情页渲染测试
- [ ] 增加可访问性基础检查

## P2：before / after 对比可视化

- [ ] 新增 web_comparison_reader.py
- [ ] 读取 report-comparison.json 与 report-comparison.md
- [ ] 展示 before / after 包摘要
- [ ] 展示 resolved / unresolved / new / changed signals
- [ ] 高亮 not_verified 与 candidate_verified 状态
- [ ] 支持从 verification 页面跳转到 comparison 页面
- [ ] 支持缺失 comparison 时提示下一步 compare 命令
- [ ] 增加 comparison reader 测试
- [ ] 增加 comparison HTML 渲染测试

## P2：Evidence 详情体验

- [ ] 支持安全预览日志文件
- [ ] 支持安全预览命令输出 JSON
- [ ] 支持安全预览 test-results JSON
- [ ] 支持安全预览 media probe 结果
- [ ] 支持附件列表展示但不直接内嵌未知二进制
- [ ] 支持证据 ID 到文件路径的映射
- [ ] 支持从 timeline / ai-task / verification 跳转到 evidence 详情
- [ ] 对可能含敏感信息的证据显示 redaction 状态提醒
- [ ] 增加 evidence preview 测试

## P2：验证工作台

- [ ] 显示 verification_result.status 的视觉状态
- [ ] 显示缺失证据清单
- [ ] 显示必须重跑的测试
- [ ] 显示建议下一步命令
- [ ] 显示 report_comparison_status 与 vly_core_proof_status
- [ ] 显示用户确认问题是否已有对应测试记录
- [ ] 不允许 UI 文案在缺证据时宣称“已修复”
- [ ] 增加 verification workbench 测试

## P2：本地审阅与备注模式（后续决策项）

- [ ] 设计 review notes 数据结构
- [ ] 写 ADR：是否允许 Web UI 写回诊断包
- [ ] 若允许写回，必须记录 reviewer、时间、内容、来源页面
- [ ] 支持只读模式与显式写回模式区分
- [ ] 支持导出 review notes 到诊断包
- [ ] 增加 review mode 测试

## P2：质量保障与发布准备

- [ ] 增加 P2 Web UI 端到端 smoke
- [ ] 增加多诊断包样例 fixture
- [ ] 增加缺失文件 / 损坏 JSON / 空 evidence 场景测试
- [ ] 增加 README.zh-CN.md P2 完整工作台说明
- [ ] 增加 README.en.md P2 完整工作台说明
- [ ] Issue #15 全部完成后关闭
- [ ] 准备版本发布说明草稿，但不发布版本

## P3-P5：后续路线图入口

- [x] 新建 P3 Issue：AI Coding Collaboration Layer
- [x] 新建 P4 Issue：Automated Diagnosis Pipeline
- [x] 新建 P5 Issue：Productization and Release Readiness
- [x] 新增 ADR：P3-P5 Roadmap
- [x] 新增 `docs/roadmap/p3-p5.md`
- [x] 新增 `TODO-P3-P5.md`
- [ ] P3 完成后关闭 Issue #18
- [ ] P4 完成后关闭 Issue #19
- [ ] P5 完成后关闭 Issue #20

详细执行清单见：`TODO-P3-P5.md`。

## P6：诊断协议标准化与生态平台路线图入口

- [x] 新建 P6 Issue：Diagnostic Protocol Standardization and Ecosystem Platform
- [x] 新增 ADR：P6 Standardization and Ecosystem Roadmap
- [x] 新增 `docs/roadmap/p6.md`
- [x] 新增 `TODO-P6.md`
- [ ] 获得明确授权后才启动 P6 实现开发
- [ ] P6 完成后关闭 Issue #22

详细执行清单见：`TODO-P6.md`。

## 工作规则

1. 所有代码改动必须对应 TODO 或 Issue。
2. 架构方向变化必须写入 `docs/adr/`。
3. 每次完成一个任务，必须更新本文件。
4. 不允许只靠记忆推进项目。
