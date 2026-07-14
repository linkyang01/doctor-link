# Doctor link

**语言 / Language：** [English](README.en.md) | 中文

Doctor link 是一个面向软件项目的人机协同诊断层。它服务于非程序员用户、开发者和 AI 编程工具，让人和 AI 可以围绕同一个问题、同一组证据、同一个验证标准进行协作。

Doctor link 不替代 Codex、Aider、OpenHands、Continue、Cursor 或其它 AI 编码工具。它的目标是为这些工具准备高质量的诊断上下文，让 AI 在修复问题时少猜、少乱改、可验证。

当前源码提供 `doctor-link solve`：针对干净 Git 仓库中的 Python 或 Node.js JavaScript/TypeScript 项目，先真实复现问题并生成修复预演；用户显式传入 `--allow-repair` 后，Doctor link 才创建独立分支、调用 Codex、最多迭代三轮，并独立重跑全部必选命令。测试、包清单与锁文件、测试配置、复现与测试目录文件，以及检查命令直接引用的脚本都会先做哈希保护；Codex 说“已修复”或削弱测试都不算成功，只有在保护输入未变化的前提下重测全部通过才返回 `verified`。

## 当前状态

Doctor link 已完成 P0-P6 的协议、Schema、产品化和生态规范工作，P7 已将前期规划中的本地运行能力转化为真实可执行、可测试、可文档化的 CLI 能力。Post-P7 加固修复也已完成。

P5：Productization and Release Readiness 已完成。P6 实现开发需要单独明确授权，尤其是托管服务、外部账号、发布、真实签名密钥、marketplace 或企业集成行为。

P7.10 增加最终验证与收口层，包括 P7 runtime 验证脚本，以及覆盖 P7 命令面的 CI 校验。

版本 [`v0.5.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.5.0) 是当前最新正式版本，增加自然语言问题复现、`doctor-link assist` 引导入口和 24 项 Python/Node.js 长期基准；用户不再必须理解测试命令。

Doctor link 仍然坚持本地优先。版本 `0.5.0` 已通过 363 项测试、85.06% 分支覆盖率、全部 66 个安装后 CLI 入口、75 次真实调用、12 个复杂场景，以及 Python 3.10–3.14、Ubuntu/macOS/Windows、安全检查、构建与隔离安装。[最终 PR CI 29305470580](https://github.com/linkyang01/doctor-link/actions/runs/29305470580) 的 10 个作业全部通过。PR [#150](https://github.com/linkyang01/doctor-link/pull/150) 合并为 `ac5c2f5`；[发布工作流 29305612221](https://github.com/linkyang01/doctor-link/actions/runs/29305612221) 创建不可变 GitHub Release，PyPI 步骤保持关闭。

当前验证修复路径支持干净 Git 仓库中的 Python 与 Node.js JavaScript/TypeScript 项目；Node.js 修复还需要项目对应的运行时和包管理器。自动修改必须安装并登录 Codex CLI，并由用户显式传入 `--allow-repair`。其他语言生态和 PyPI 安装暂不支持。完整规则见[Codex 自动解决](../automatic-solve.md)、[自动诊断可靠性](../automated-diagnosis-reliability.md)和[全能力验证](../full-capability-validation.md)。

## 常用命令

```bash
doctor-link wizard --folder . --tool cursor
doctor-link assist /path/to/project --problem "结算重复扣款"
doctor-link reproduce suggest /path/to/project --problem "结算重复扣款" --json
doctor-link preflight . --json
doctor-link solve /path/to/python-project --problem "结算重复扣款" --test-command "python -m pytest tests/test_checkout.py -q"
doctor-link solve /path/to/python-project --problem "结算重复扣款" --test-command "python -m pytest tests/test_checkout.py -q" --allow-repair
doctor-link solve /path/to/node-project --problem "并发更新导致数据丢失" --test-command "npm test" --allow-repair
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link reproduce run <id> . --package-dir <package_dir> --json
doctor-link test run . --package-dir <package_dir> --json
doctor-link verify <package_dir> --write-back
doctor-link handoff list
doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ci report DoctorReports --out DoctorReports/ci --json
doctor-link distribution check . --dist dist --out DoctorReports/distribution --json
doctor-link adapter run demo-adapter verification . --allow-run --json
doctor-link plugin run demo-plugin verification . --allow-run --json
doctor-link integrity verify . DoctorReports/integrity-manifest.json --strict --json
doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json --json
doctor-link archive create DoctorReports-source DoctorReports/archive --metadata owner=qa --json
```

Adapter 和 Plugin 的 `run` 命令默认只做 dry-run，不执行配置的本地命令。默认模式会校验 manifest 并写入运行/审计记录。只有在用户审查 manifest 后显式传入 `--allow-run`，才会真正执行本地命令。

## 验证入口

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-branch --cov-fail-under=85
bandit -r doctor_link -ll
pip-audit
python -m build
python scripts/validate_distribution_contents.py dist
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
python examples/full-capability-lab/run-all.py --dist dist
```

## 文档入口

- `../installation.md`
- `../quick-start.md`
- `../cli-reference.md`
- `../automated-diagnosis-reliability.md`
- `../automatic-solve.md`
- `../full-capability-validation.md`
- `../platform-integration-roadmap.zh-CN.md`
- `../github-repository-guide.md`
- `../project-status.md`
- `../validation/local-quality-scorecard.md`
- `../p7-final-audit.md`
- `../p7-self-validation.md`
- `../acceptance-review.md`
- `../archive/completed-todos/README.md`

## Runtime 覆盖范围

P7 已实现证据加固、本地工作台加固、AI handoff runtime、CI 自动化、分发就绪检查、Adapter runtime、Plugin runtime、完整性与隐私门禁、本地知识索引、本地归档辅助能力。当前源码已在这些地基上把自动解决纵切面扩展到 Python 与 Node.js JavaScript/TypeScript 项目。

## 边界说明

Doctor link 当前不提供托管 Web 平台、云同步、外部账号体系、遥测、marketplace、真实签名密钥或密钥管理、托管企业归档、托管诊断知识库或真实 RBAC。自动修复当前支持 Python 与 Node.js JavaScript/TypeScript 项目，必须显式授权，保护原始验收输入，不自动提交、推送或发布；其他语言生态只有具备同等可测试的适配后才会纳入。例外参数 `--allow-verification-changes` 只能得到 `review_required`，不能得到 `verified`。`--allow-repair` 会使用已有 Codex 登录调用服务，用户应先审查预演并移除敏感信息。PyPI 发布仍为可选项。
