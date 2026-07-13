# Doctor link 非程序员快速入门（中文）

Doctor link 帮你在**不写代码**的情况下，收集软件问题的证据，并生成可以给 AI 编程工具或开发者使用的修复材料包。

## Doctor link 会生成什么

- **诊断包**文件夹：包含报告、证据和下一步建议。
- 可选的 **HTML 报告**：用浏览器打开即可查看。
- 可选的 **AI 交接包**：可以直接交给 Cursor 等 AI 工具。

## 第一步 — 安装

先克隆仓库并进入 `doctor-link` 目录，再执行：

```bash
python3 --version
pip install -e .
doctor-link --version
```

需要 Python 3.10–3.14。

## 第二步 — 运行向导（推荐）

```bash
doctor-link wizard
```

向导会依次询问：

1. 要检查哪个文件夹
2. 你遇到什么问题
3. 是否自动收集日志
4. 是否生成 AI 交接包

结束后会明确告诉你：**打开哪个报告、分享哪个文件夹**。

## 第三步 — 或用一条命令

```bash
doctor-link diagnose-now /你的项目路径 --full --summary "简短问题描述"
```

需要同时生成 AI 包时加上 `--handoff`：

```bash
doctor-link diagnose-now /你的项目路径 --full --handoff --summary "登录失败"
```

## 第四步 — 查看结果

```bash
doctor-link home --reports DoctorReports
```

用浏览器打开输出的 `index.html`。

## 发给 AI 的内容

把 `wizard` 或 `diagnose-now --handoff` 输出的 **handoff 文件夹** 发给 AI 工具。

不要发送：

- 无关的个人文件；
- 生产环境密钥；
- 整盘备份。

## 命令失败时怎么办

| 情况 | 处理方式 |
|------|----------|
| 文件夹不存在 | 检查路径后重试 |
| Python 版本过低 | 安装 Python 3.10+ |
| 找不到诊断包 | 先运行 `doctor-link report .` |
| 没有写入权限 | 换一个你有权限的目录 |

## 开发者下一步

完整 CLI 流程见 `docs/quick-start.md`。
