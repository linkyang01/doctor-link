# Doctor link TODO

本文件用于项目化跟踪 Doctor link 的阶段状态。详细任务以专项 TODO、Issue、ADR 和审计文档为准。

## 当前阶段状态

- [x] P0：Diagnostic Foundation
- [x] P1：Evidence Collection Primitives
- [x] P1+：CLI Evidence Pipeline
- [x] P2：Local Read-only Diagnostic Workbench
- [ ] P2+：Mainline Diagnostic Workbench Enhancements
- [ ] P3：AI Coding Collaboration Layer
- [ ] P4：Automated Diagnosis Pipeline
- [ ] P5：Productization and Release Readiness
- [ ] P6：Diagnostic Protocol Standardization and Ecosystem Platform

## P0：Diagnostic Foundation

状态：完成。

完成内容：

- [x] 项目管理地基
- [x] 诊断协议核心模型
- [x] 标准诊断包生成器
- [x] 用户确认问题机制
- [x] 问题地图
- [x] AI 修复任务生成
- [x] 修复验证清单
- [x] `.doctorlink` 项目配置协议基础模板

关键文件：

- `doctor_link/core/models.py`
- `doctor_link/core/package_builder.py`
- `doctor_link/core/user_assertion_manager.py`
- `doctor_link/core/problem_map_builder.py`
- `doctor_link/core/ai_task_generator.py`
- `doctor_link/core/verification_builder.py`
- `.doctorlink/`

## P1：Evidence Collection Primitives

状态：完成。

完成内容：

- [x] 环境证据采集
- [x] 命令输出采集
- [x] 日志采集
- [x] 媒体探测
- [x] 测试结果记录
- [x] Vly Proof Adapter
- [x] before / after 报告对比
- [x] P1 测试与 CLI smoke

关键命令：

- `doctor-link env`
- `doctor-link probe`
- `doctor-link record`
- `doctor-link vly-proof`
- `doctor-link compare`

## P1+：CLI Evidence Pipeline

状态：完成。

完成内容：

- [x] `doctor-link collect`
- [x] `doctor-link verify`
- [x] `doctor-link doctor-package`
- [x] 诊断包打包与 manifest
- [x] 敏感信息过滤与报告
- [x] `.doctorlink` 配置增强
- [x] CLI 参数覆盖配置文件
- [x] assertion-linked test records
- [x] assertion coverage in verification
- [x] P1/P1+ 审计文档

关键文件：

- `doctor_link/core/collector.py`
- `doctor_link/core/verification_runner.py`
- `doctor_link/core/package_exporter.py`
- `doctor_link/core/redactor.py`
- `doctor_link/core/config_loader.py`
- `doctor_link/core/test_recorder.py`
- `docs/p1-p1plus-audit.md`
- `TODO-P1-P1PLUS-HARDENING.md`

## P2：Local Read-only Diagnostic Workbench

状态：完成。

完成内容：

- [x] 本地只读 Web UI 边界 ADR
- [x] 单诊断包浏览
- [x] 多诊断包 `DoctorReports` 索引
- [x] 诊断包详情工作台
- [x] Overview / Timeline / Evidence / Assertions / AI Task / Verification / Comparison / Redaction / Manifest / Raw Files 视图
- [x] dedicated comparison reader
- [x] before / after comparison display
- [x] evidence anchors and cross-links
- [x] evidence preview safety behavior
- [x] verification signals panel
- [x] assertion coverage display in workbench
- [x] redaction and manifest review panels
- [x] P2 final audit
- [x] P2 draft release notes
- [x] Issue #15 closed as completed

关键文件：

- `doctor_link/core/web_package_reader.py`
- `doctor_link/core/web_detail_renderer.py`
- `doctor_link/core/web_comparison_reader.py`
- `doctor_link/core/reports_indexer.py`
- `doctor_link/core/web_server.py`
- `docs/p2-hardening-plan.md`
- `docs/p2-final-audit.md`
- `docs/release-notes/p2-draft.md`
- `TODO-P2-HARDENING.md`

## P2+：Mainline Diagnostic Workbench Enhancements

状态：已纳入主线，正在规划与实施。

说明：P2+ 不是独立长期阶段，而是 P2 完成后的主线增强任务组，重点增强本地诊断工作台、Evidence 审阅、Verification 工作台、AI Task Handoff、Web UI 可用性和样例诊断包。

边界：本地 Web UI 默认保持只读。任何写回能力必须另写 ADR 并保持显式操作。

- [x] 新增 P2+ Issue：Mainline Diagnostic Workbench Enhancements
- [x] 新增 `TODO-P2PLUS.md`
- [x] 新增 `docs/roadmap/p2plus.md`
- [x] 新增 ADR：P2+ Mainline Enhancement
- [ ] P2+ 完成后关闭 Issue #37

详细执行清单见：`TODO-P2PLUS.md`。

## P2 Deferred Decision：Review Notes / Write-back Mode

状态：未启动，保留为后续显式决策项。

说明：P2 当前保持本地只读。任何 Web UI 写回能力必须另写 ADR，并且必须保持显式操作，不允许默认写回。

- [ ] 设计 review notes 数据结构
- [ ] 写 ADR：是否允许 Web UI 写回诊断包
- [ ] 若允许写回，记录 reviewer、时间、内容、来源页面
- [ ] 支持只读模式与显式写回模式区分
- [ ] 支持导出 review notes 到诊断包
- [ ] 增加 review mode 测试

## P1 / P1+ / P2 Final Audit

状态：完成。

- [x] P1 完成状态确认
- [x] P1+ 完成状态确认
- [x] P2 完成状态确认
- [x] P1/P1+/P2 final audit 入库
- [x] Issue #31 closed as completed

关键文件：

- `docs/p1-p2-final-audit.md`

## P3-P5：后续路线图入口

状态：已规划，未启动实现。

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

状态：已规划，未启动实现。

- [x] 新建 P6 Issue：Diagnostic Protocol Standardization and Ecosystem Platform
- [x] 新增 ADR：P6 Standardization and Ecosystem Roadmap
- [x] 新增 `docs/roadmap/p6.md`
- [x] 新增 `TODO-P6.md`
- [ ] 获得明确授权后才启动 P6 实现开发
- [ ] P6 完成后关闭 Issue #22

详细执行清单见：`TODO-P6.md`。

## 工作规则

1. 所有代码改动必须对应 TODO、Issue 或审计文档。
2. 架构方向变化必须写入 `docs/adr/`。
3. 每次完成一个任务，必须更新对应追踪文件。
4. 不允许只靠记忆推进项目。
5. 不发布版本、不创建 GitHub Release、不发布包仓库，除非获得明确授权。
