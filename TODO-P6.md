# Doctor link P6 TODO

本文件用于跟踪 Doctor link P6：诊断协议标准化与生态平台。每完成一项，必须把对应任务从 `[ ]` 改为 `[x]`。

关联文件：

- P6 Issue: #22
- Roadmap: `docs/roadmap/p6.md`
- P6.1 Schema v1: `docs/p6-schema-v1.md`
- P6.2 Conformance: `docs/p6-conformance.md`
- P6.3 Adapter SDK Planning: `docs/p6-adapter-sdk.md`
- P6.4 Plugin SDK Planning: `docs/p6-plugin-sdk.md`
- P6.5 AI Coding Integrations: `docs/p6-ai-coding-integrations.md`
- P6.6 Signing and Integrity: `docs/p6-signing-integrity.md`
- P6.7 Privacy and Security: `docs/p6-privacy-security.md`
- P6.8 Enterprise Governance: `docs/p6-enterprise-governance.md`
- Schema files: `schemas/v1/`

P6 已完成 P6.1 schema 标准化、P6.2 本地兼容性与一致性测试套件、P6.3 Adapter SDK 规划规范、P6.4 Plugin SDK 规划规范、P6.5 第三方 AI Coding 集成规范、P6.6 签名与完整性规划规范、P6.7 隐私与安全分级规范、P6.8 企业归档与治理模型规范。当前不启动 Web 平台、云服务、账号体系、市场平台、真实第三方集成、真实签名实现、真实权限系统、企业归档系统、Adapter SDK 运行时或 Plugin SDK 运行时。

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

- [x] 定义 adapter lifecycle
- [x] 定义 adapter metadata format
- [x] 定义 adapter capability declaration
- [x] 定义 adapter evidence collector interface
- [x] 定义 adapter verification provider interface
- [x] 定义 adapter handoff provider interface
- [x] 定义 adapter test requirements
- [x] 编写 first-party adapter rules
- [x] 编写 third-party adapter rules

## P6.4 Plugin SDK planning

- [x] 定义 plugin package structure
- [x] 定义 plugin manifest format
- [x] 定义 plugin permission model
- [x] 定义 plugin loading boundary
- [x] 定义 plugin security restrictions
- [x] 定义 collector plugin extension point
- [x] 定义 renderer plugin extension point
- [x] 定义 handoff plugin extension point
- [x] 定义 verification plugin extension point
- [x] 增加 plugin compatibility checklist

## P6.5 Third-party AI Coding integration specification

- [x] 定义 generic AI tool handoff protocol
- [x] 定义 Codex integration specification
- [x] 定义 Cursor integration specification
- [x] 定义 Continue integration specification
- [x] 定义 Aider integration specification
- [x] 定义 OpenHands integration specification
- [x] 定义 Claude Code integration specification
- [x] 定义 integration test package format
- [x] 定义 minimum tool capability requirements
- [x] 定义 unsupported integration behavior

## P6.6 Diagnostic package signing and integrity

- [x] 定义 package content hashing model
- [x] 定义 manifest integrity fields
- [x] 定义 package signature metadata
- [x] 定义 signing key policy
- [x] 规划 verification command
- [x] 定义 tamper detection behavior
- [x] 定义 signed package export checklist
- [x] 增加 security review requirements

## P6.7 Privacy and security level specification

- [x] 定义 diagnostic package privacy levels
- [x] 定义 evidence sensitivity levels
- [x] 定义 redaction levels
- [x] 定义 export safety levels
- [x] 定义 enterprise sharing policy model
- [x] 定义 external AI handoff privacy warning rules
- [x] 定义 sensitive evidence preview restrictions
- [x] 增加 privacy documentation requirements

## P6.8 Enterprise archive and governance model

- [x] 定义 diagnostic package retention policy format
- [x] 定义 archive metadata model
- [x] 定义 project-level audit trail model
- [x] 定义 reviewer roles
- [x] 定义 approval states
- [x] 定义 team review workflow
- [x] 定义 enterprise export policy
- [x] 定义 deletion and retention boundaries

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
- [ ] 获得明确授权后才启动 P6.9+ 实现开发
- [ ] P6 Issue #22 全部完成后关闭
