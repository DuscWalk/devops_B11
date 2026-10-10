# 协作约定

## 分工

DRAFT 负责人孙静怡，MDFixer 负责人王硕，接口与联调负责人胡博。分工与实际贡献见 `e2/CONTRIBUTIONS.md`；技术提议须由相关成员与 A11 确认。

## 开发流程

- 从最新 `main` 创建任务分支，使用 `feat/`、`fix/` 或 `docs/` 前缀。
- 一个 Merge Request 聚焦一个任务，写明变更、验证方法及未完成内容。
- 建议由另一名成员审阅后合并。当前尚未配置 GitLab 分支保护或强制审批。
- 提交说明可使用 `feat(draft): ...`、`feat(mdfixer): ...`、`docs(e2): ...`。
- 不提交令牌、密码、本地环境、镜像归档或大型运行产物。

## 接口变更

先与 A11 确认消费者影响，再同步 Schema、样例与版本记录。未确认的方案明确标记为待确认。

## 验证与贡献

每项任务记录可复现的验证命令或人工检查步骤。只记录实际运行结果；示例中的成功值不算运行证据。成员按真实贡献记录提交 SHA 或 Merge Request 链接。

## E2 提交基线

当前交付版本见 e2/SUBMISSION.md；后续从最新 main 创建功能分支。原始来源/证据不得直接改写为当前结果，接口变更同步 Schema、样例、校验与 CHANGELOG。提交前运行 `.venv/bin/python e2/validate.py`，保留真实失败/限制。

## E3 协作

公共底座分支 `feat/e3-hubo-baseline`；模块负责人从该分支建立自己的 E3 任务分支，见 `e3/HANDOFF.md`。原 `e2/` 为历史快照，不改写其证据。模块材料分别在 draft/、mdfixer/ 追加；每人导出独立证据目录，公共 STATUS/Backlog 由胡博汇总以减少冲突。

提交前运行 `.venv/bin/python e3/scripts/run_baseline.py`；DRAFT 同时记录 `verify_docker.py` 的结果。参考答案必须标 ORACLE 来源，实际日志和人工预期分开；不可把本地读取当 A11 接收、参考 Patch 当工具自动生成。保留原作者历史，不提交 e3/work、镜像、凭据。
