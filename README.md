# DevOps B11

B11 小组协作仓库，负责 DRAFT（生成可构建环境）和 MDFixer（修复缺失依赖）。配对组为 A11，负责 BuildChecker 和 EChecker。

## 当前状态

已完成 E2 本地准备：登记成员、保存 A11 原始快照、审阅契约、准备读取演示与校验、整理待沟通问题。DRAFT/MDFixer 尚未实现，公共契约尚未由双方确认。

- 孙静怡：DRAFT；王硕：MDFixer；胡博：接口与联调。
- [E2 材料与验证](e2/README.md)：原校验 42/42；扩展审阅发现增量查询遗漏字段，修正提议另存。
- [DRAFT 回复已收到](e2/feedback/draft-2026-09-21.md)：孙静怡 feat/draft 的样例通过校验，5 个文件可读取；手工镜像基线已留证，尚待 A11 接受和交付。
- [现在需要沟通的内容](e2/PAIRING.md)：汇总给 A11 的文字、王硕待回复项、三轮练习和决定登记表。

## 目录

- `e2/`：B 组 E2 材料、任务和协商记录。
- `draft/`：DRAFT 实现与使用说明。
- `mdfixer/`：MDFixer 实现与使用说明。
- `fixtures/`：固定 MD 报告、项目版本及样本来源。
- `CONTRIBUTING.md`：分支、提交和 Merge Request 约定。

## 开始协作

1. 克隆本仓库，阅读 `e2/Backlog.md`，认领任务并记录负责人。
2. 从最新 `main` 创建任务分支，如 `feat/draft-environment` 或 `feat/mdfixer-input`。
3. 完成工作并验证，在 GitLab 提交 Merge Request，由另一位组员审阅。
4. 合并后更新任务状态和个人贡献记录。

## 与 A11 的接口

A 组参考仓库：https://git.nju.edu.cn/devops-group11/devops-group11

已核实参考版本：`96f35cc175d12f51f3f7f0915ba35a98d303fcb3`，原材料保存在 [e2/reference/](e2/reference/README.md)。该快照供审阅，不代表 B11 已接受全部约定。双方确认字段、产物读取方式和修正后，再固定正式共享版本。

E2 先完成契约和样例，不要求部署 API。E3 准备 DRAFT 项目和固定 MD 报告。
