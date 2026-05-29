# Doctor link P6 TODO

本文件用于跟踪 Doctor link P6：诊断协议标准化与生态平台。每完成一项，必须把对应任务从 `[ ]` 改为 `[x]`。

关联文件：

- P6 Issue: #22
- Roadmap: `docs/roadmap/p6.md`
- P6.1 Schema v1: `docs/p6-schema-v1.md`
- P6.2 Conformance: `docs/p6-conformance.md`
- Schema files: `schemas/v1/`

P6 已从 P6.1 schema 标准化开始，并完成 P6.2 本地兼容性与一致性测试套件。当前不启动 Web 平台、云服务、账号体系、市场平台、Adapter SDK 或 Plugin SDK。

---

## P6.1 Diagnostic Package Schema v1

- [x] 定义 `doctor-report.json` JSON Schema
- [x] 定义 `ai-context.json` JSON Schema
- [x] 定义 `user-assertions.json` JSON Schema
- [x] 定义 `verification-result.json` JSON Schema
- [x] 定义 `manifest.json` JSON Schema
- [x] P3 完成后定义 `ai-repair-result.json` JSON Schema
- [x] P3 完成后定义 `diagnosis-history.json` JSON Schema
- [x] 定义 package schema version 字段
- [x] 定义 schema compatibility policy
- [x] 定义 schema migration policy
- [x] 增加 schema validation command
- [x] 增加 schema validation fixtures / tests

## P6.2 Compatibility and conformance test suite

- [x] 定义 valid diagnostic package fixture set
- [x] 定义 invalid diagnostic package fixture set
- [x] 定义 backward compatibility fixture set
- [x] 定义 schema migration fixture set
- [x] 定义 conformance report format
- [x] 定义 compatibility score model
- [x] 规划并接入 conformance tests CI
- [x] 编写 compatibility guarantees 文档

## P6.3 Adapter SDK planning

- [ ] 定义 adapter lifecycle
- [ ] 定义 adapter metadata format
- [ ] 定义 adapter capability declaration
- [ ] 定义 adapter evidence collector interface
- [ ] 定义 adapter verification provider interface
- [ ] 定义 adapter handoff provider interface
- [ ] 定义 adapter test requirements
- [ ] 编写 first-party adapter rules
- [ ] 编写 third-party adapter rules

## P6.4 Plugin SDK planning

- [ ] 定义 plugin package structure
- [ ] 定义 plugin manifest format
- [ ] 定义 plugin permission model
- [ ] 定义 plugin loading boundary
- [ ] 定义 plugin security restrictions
- [ ] 定义 collector plugin extension point
- [ ] 定义 renderer plugin extension point
- [ ] 定义 handoff plugin extension point
- [ ] 定义 verification plugin extension point
- [ ] 增加 plugin compatibility checklist

## P6.5 Third-party AI Coding integration specification

- [ ] 定义 generic AI tool handoff protocol
- [ ] 定义 Codex integration specification
- [ ] 定义 Cursor integration specification
- [ ] 定义 Continue integration specification
- [ ] 定义 Aider integration specification
- [ ] 定义 OpenHands integration specification
- [ ] 定义 Claude Code integration specification
- [ ] 定义 integration test package format
- [ ] 定义 minimum tool capability requirements
- [ ] 定义 unsupported integration behavior

## P6.6 Diagnostic package signing and integrity

- [ ] 定义 package content hashing model
- [ ] 定义 manifest integrity fields
- [ ] 定义 package signature metadata
- [ ] 定义 signing key policy
- [ ] 规划 verification command
- [ ] 定义 tamper detection behavior
- [ ] 定义 signed package export checklist
- [ ] 增加 security review requirements

## P6.7 Privacy and security level specification

- [ ] 定义 diagnostic package privacy levels
- [ ] 定义 evidence sensitivity levels
- [ ] 定义 redaction levels
- [ ] 定义 export safety levels
- [ ] 定义 enterprise sharing policy model
- [ ] 定义 external AI handoff privacy warning rules
- [ ] 定义 sensitive evidence preview restrictions
- [ ] 增加 privacy documentation requirements

## P6.8 Enterprise archive and governance model

- [ ] 定义 diagnostic package retention policy format
- [ ] 定义 archive metadata model
- [ ] 定义 project-level audit trail model
- [ ] 定义 reviewer roles
- [ ] 定义 approval states
- [ ] 定义 team review workflow
- [ ] 定义 enterprise export policy
- [ ] 定义 deletion and retention boundaries

## P6.9 Cross-project diagnostic knowledge base

- [ ] 定义 problem taxonomy
- [ ] 定义 reproduction pattern taxonomy
- [ ] 定义 verification pattern taxonomy
- [ ] 定义 repair outcome taxonomy
- [ ] 定义 recurring failure signature model
- [ ] 定义 AI repair quality metrics
- [ ] 定义 project health trend metrics
- [ ] 定义 knowledge export format
- [ ] 定义 privacy boundaries for cross-project learning

## P6.10 Public ecosystem assets

- [ ] 定义 public example diagnostic package library
- [ ] 定义 template catalog structure
- [ ] 定义 adapter catalog structure
- [ ] 定义 plugin catalog structure
- [ ] 定义 compatibility badge rules
- [ ] 定义 contribution guide for examples
- [ ] 定义 contribution guide for adapters
- [ ] 定义 contribution guide for plugins
- [ ] 定义 ecosystem documentation index

## P6.11 P6 quality and closure

- [ ] 增加 P6 conformance fixture plan
- [ ] 增加 P6 documentation review checklist
- [ ] 增加 P6 security review checklist
- [ ] 增加 P6 compatibility review checklist
- [ ] 更新 README.zh-CN.md 的 P6 roadmap summary
- [ ] 更新 README.en.md 的 P6 roadmap summary
- [ ] 获得明确授权后才启动 P6.3+ 实现开发
- [ ] P6 Issue #22 全部完成后关闭
