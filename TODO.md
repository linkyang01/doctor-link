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

## P2：本地 Web UI / 诊断包浏览器

- [x] 新建 GitHub Issue：P2 Local Web UI / Diagnostic Package Browser
- [x] 新增 ADR：Local Web UI Boundary
- [ ] 新增 web package reader
- [ ] 新增静态 HTML 渲染器
- [ ] 支持读取 summary / timeline / evidence / assertions / ai-task / verification
- [ ] 支持读取 redaction report / manifest / package readme
- [ ] 新增 doctor-link view 命令
- [ ] 支持 --host / --port / --no-open-browser
- [ ] 保持本地只读浏览，不修改诊断包
- [ ] 增加 package reader 测试
- [ ] 增加 HTML renderer 测试
- [ ] 增加 view CLI 烟测
- [ ] 更新 README.zh-CN.md
- [ ] 更新 README.en.md

## 工作规则

1. 所有代码改动必须对应 TODO 或 Issue。
2. 架构方向变化必须写入 `docs/adr/`。
3. 每次完成一个任务，必须更新本文件。
4. 不允许只靠记忆推进项目。
