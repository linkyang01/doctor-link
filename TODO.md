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
- [ ] 建立 issue 模板

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

- [ ] 新增 package_builder.py
- [ ] 生成标准 DoctorReports 目录
- [ ] 生成 summary.md
- [ ] 生成 problem-map.md
- [ ] 生成 timeline.md
- [ ] 生成 evidence-list.md
- [ ] 生成 doctor-report.json
- [ ] 生成 ai-context.json
- [ ] 生成 user-assertions.json

## P0：用户确认问题机制

- [ ] 新增 user_assertion_manager.py
- [ ] 增加 doctor-link assert 命令
- [ ] 支持用户声明 expected_behavior
- [ ] 支持用户声明 actual_behavior
- [ ] 支持用户声明 why_user_thinks_it_is_wrong
- [ ] 让 ai-task.md 强制包含用户确认问题

## P0：问题地图与 AI 任务

- [ ] 新增 problem_map_builder.py
- [ ] 输出 problem-map.md
- [ ] 升级 ai_task_generator.py
- [ ] 增加 investigation-boundary.md
- [ ] 新增 verification_builder.py
- [ ] 输出 fix-verification-checklist.md

## P0：项目配置协议

- [ ] 新增 .doctorlink/doctorlink.yml 模板
- [ ] 新增 .doctorlink/test-matrix.yml 模板
- [ ] 新增 .doctorlink/assertions.yml 模板
- [ ] 新增 .doctorlink/verification.yml 模板

## P1：证据采集能力

- [ ] 新增 environment_collector.py
- [ ] 新增 command_runner.py
- [ ] 新增 log_collector.py
- [ ] 新增 media_probe.py
- [ ] 新增 test_recorder.py

## P1：Vly Adapter

- [ ] 定义 Vly Core Proof 测试矩阵
- [ ] 支持 VlyTestLibrary 扫描
- [ ] 支持 ffprobe 读取媒体信息
- [ ] 支持播放测试结果记录
- [ ] 支持 Go / No-Go 评估

## 工作规则

1. 所有代码改动必须对应 TODO 或 Issue。
2. 架构方向变化必须写入 `docs/adr/`。
3. 每次完成一个任务，必须更新本文件。
4. 不允许只靠记忆推进项目。
