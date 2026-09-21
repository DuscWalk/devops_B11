# B11 贡献记录

## 分工

以下分工来自胡博于 2026-09-21 提供的信息。

| 成员 | 职责 |
| --- | --- |
| 孙静怡 | DRAFT 输入输出确认、DRAFT 项目准备 |
| 王硕 | MDFixer 输入输出确认、固定 MD 报告准备 |
| 胡博 | 公共契约确认、产物读取约定、三轮配对练习组织、契约校验 |
| 全体 | 各自的验证、提交与贡献记录 |

## 本轮实际准备

| 负责人 | 实际工作 | 证据 | 状态 |
| --- | --- | --- | --- |
| 胡博（Codex 辅助） | 核对 A11 来源提交，保留 13 文件原始快照和逐文件摘要 | reference/README.md、a11-source.json | 已完成本地核对 |
| 胡博（Codex 辅助） | 审阅公共模型与交接问题，发现增量查询遗漏 configuration_id，准备单字段修正 | CONTRACT_REVIEW.md、proposals/、ADR.md | 提议待成员/A11 确认 |
| 胡博（Codex 辅助） | 建立分类型输入检查、文件读取演示和 17 个回归检查，记录原件失败和提议通过 | validate.py、artifact_access.py、tests/、evidence/ | 本地验证完成；非端到端工具运行 |
| 胡博（Codex 辅助） | 登记分工，准备三轮练习与沟通草稿 | Backlog.md、PAIRING.md、STATUS.md、AI_USAGE.md | 待胡博人工审阅并发起沟通 |
| 孙静怡 | 待本人追加实际完成内容 | 待本人提交 | 不由本次准备代记完成 |
| 王硕 | 待本人追加实际完成内容 | 待本人提交 | 不由本次准备代记完成 |

## 来源与提交

- A11 原材料属于 A11，来源提交 `96f35cc175d12f51f3f7f0915ba35a98d303fcb3`，不登记为 B11 原创。
- B11 仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11 。本轮基于 `5cacba9451863ebf7c794df9374276f88eff1fb4`，分支 `docs/e2-contract-alignment`。
- 本轮准备提交：`4f88d13a126608854a5ba7ac062d169af4780e75`（`feat(e2): prepare B11 contract review and offline validation`），包含本次材料、代码和验证证据。本条记录在后续文档提交中回填，避免引用尚未产生的 SHA。
- 提交身份使用 `duscwalk <241276007@smail.nju.edu.cn>`，本轮任务负责人对应胡博。没有改写他人的历史提交。
- 远端推送、MR、成员审阅和配对沟通尚未发生；不编造相关链接或确认记录。
