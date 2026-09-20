# DevOps B11

B11 小组协作仓库，负责 DRAFT（生成可构建环境）和 MDFixer（修复缺失依赖）。配对组为 A11，负责 BuildChecker 和 EChecker。

## 当前状态

已初始化目录和协作约定。工具尚未实现，E2 契约尚未由双方确认。目录中的任务清单不代表功能已经完成。

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

初始参考版本：`96f35cc`，接口材料位于其 `e2/` 目录。该版本仅是参考来源，不代表 B 组已接受全部约定。双方确认字段、产物读取方式和版本后，再将认可的契约及来源版本纳入本仓库。

E2 先完成契约和样例，不要求部署 API。E3 准备 DRAFT 项目和固定 MD 报告。
