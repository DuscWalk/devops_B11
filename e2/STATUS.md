# B11 E2 当前状态

更新：2026-09-21。当前阶段为 **已收到并审阅孙静怡 DRAFT 回复，等待 A11 对齐及王硕回复**。孙静怡分支已有手工 Docker 基线执行记录；本次仅复跑接口样例和读取检查，没有重跑 Docker。自动 DRAFT/MDFixer、修复重检和 A11 侧读取仍未完成。

## 已执行与结果

| 检查 | 命令/方法（仓库根目录） | 实际结果 |
| --- | --- | --- |
| 来源追溯 | 以 duscwalk SSH 读取 A11 main，逐字节比较 ZIP 与 e2/ | 13 文件一致；完整 SHA 见 reference/README.md |
| 原 A11 校验 | `.venv/bin/python e2/reference/a11/validate.py`（由 B11 入口执行） | 42/42；包含 9 项 Draft 2020-12 标准交叉校验 |
| 原件完整输入检查 | `.venv/bin/python e2/validate.py` | 7/8，退出 1；增量查询回显缺 configuration_id |
| 待确认修正检查 | `.venv/bin/python e2/validate.py --proposed` | 8/8 输入检查、17/17 回归检查、演示文件读取通过；整体退出 0 |
| 文件互读的本地准备 | 同上，最后一步运行 artifact_access.py | 读取 251 字节，真实摘要匹配；没有在另一组机器执行 |
| DRAFT 回复校验 | 在固定 feat/draft 提交 d7bca1e 的临时 worktree 运行 draft/validate_examples.py | 退出 0；没有改动或合并该分支 |
| DRAFT 产物读取与证据核验 | 胡博已有读取器读取 5 份交接文件；核对 Docker evidence 摘要 | 5/5 可读且摘要一致；13/13 证据摘要一致，见 [审阅](feedback/draft-2026-09-21.md) |
| 失败与 202 结构诊断 | 对原样例应用对应 `$defs`，见 JSON 证据 | 202 两字段样例缺 job_type；202 Schema 允许 RUNNING；三个错误片段均非完整 Job |

完整输出：[原件](evidence/reference-validation-2026-09-21.txt)、[提议](evidence/proposal-validation-2026-09-21.txt)、[结构诊断](evidence/reference-audit-2026-09-21.json)。初次扩展检查的完整失败信息也保留在 [初次失败记录](evidence/initial-reference-validation-2026-09-21.txt)。

测试数量分开报告：原有 42 项、提议输入 8 项、回归 17 项覆盖不同层次，存在交叉，不将它们包装成独立的端到端验收项。

## 环境与范围

- 所有日常命令、文件和 Git 操作以 duscwalk 执行；本仓库 Git 身份在本地配置。
- 实际 Python 3.10.12；项目 `.venv` 中 jsonschema 4.25.1。系统库为 3.2.0，没有 Draft202012Validator；来源脚本会将这种情况一并当作可选标准校验缺失而跳过。
- 系统缺 ensurepip。本轮用 `venv --without-pip` 创建隔离环境，再用已有系统 pip 将 pip 25.2 安装到该环境的 site-packages，随后安装 requirements。没有升级系统 Python 包。复现说明见 README。
- 所有成功值只对应上表的本地检查。A11 契约样例中的镜像大小、修复数、构建成功值仍是来源样例内容。
- 原始 Schema 和快照保持不变。补正样例和目录读取是待确认提议，不能据此宣布公共接口已冻结。

## 待沟通事项

| 项目 | 等待谁 | 下一步 |
| --- | --- | --- |
| DRAFT 字段、IMAGE 内容、日志与环境 | 胡博、A11，孙静怡跟进 | 已有 Q03/Q07 回复；确认 GCC13 候选、默认值、镜像交付和环境哈希 |
| 报告外壳、MD 过滤、补丁与重检结果 | 王硕、A11 | 回答 Q04/Q05，选择固定 MD 样本 |
| 增量查询补正、公共模型、202/失败/幂等 | 胡博、A11、两位负责人 | 确认 Q01/Q05/Q06，回写正式版本 |
| 产物实际传输及两边读取 | 胡博、A11 | 确认 Q02，再分别运行与留证 |
| 三轮练习和贡献记录 | 全体 | 按 PAIRING.md 实际执行，补日期/确认人/版本 |

下一步入口：[PAIRING.md](PAIRING.md)。fetch 已确认准备分支 e8bf6ee 和孙静怡 feat/draft 均在远端。本轮只更新本地接口记录；未合并孙静怡分支、未推送本轮更新、未代发消息或创建 MR。
