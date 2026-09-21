# B11 E2 接口准备材料

负责人：孙静怡（DRAFT）、王硕（MDFixer）、胡博（接口与联调）。配对组：A11（BuildChecker、EChecker）。

**当前状态：已收到孙静怡的 DRAFT 回复，样例校验及 5 个文件读取通过；等待 A11 对齐及王硕回复。** 详见 [DRAFT 回复审阅](feedback/draft-2026-09-21.md)。 下一步看 [PAIRING.md](PAIRING.md)，内含共享方式、两段待发消息和三轮练习记录表。E2 先定义契约和样例，尚不要求部署 API。

## 当前检查结论

A11 来源校验 **42/42 通过**。补充按任务类型检查 input 后，原件为 **7/8**：增量查询回显漏了必填 configuration_id。只补该字段的待确认提议通过 **8/8** 输入检查、**17/17** 回归检查及真实文本读取。这里的通过仅表示本地准备可复算；正式契约确认、镜像实际交付、固定 MD 报告/补丁与 A11 侧互读仍待完成。

## 文件索引

| 文件 | 用途 |
| --- | --- |
| [reference/README.md](reference/README.md)、[来源清单](reference/a11-source.json) | A11 来源 URL、完整提交、版本、ZIP 和逐文件摘要 |
| [reference/a11/task.schema.json](reference/a11/task.schema.json) | 原始 Job 与四类输入定义（参考快照） |
| [reference/a11/contract-examples.json](reference/a11/contract-examples.json) | 四类请求/响应、错误、findings 与产物元数据原样例 |
| [reference/a11/openapi.yaml](reference/a11/openapi.yaml) | 原始端点说明，仍待对齐失败视图等问题 |
| [proposals/README.md](proposals/README.md) | 待 A11 确认的单字段样例修正 |
| [feedback/draft-2026-09-21.md](feedback/draft-2026-09-21.md) | 孙静怡回复、独立复核和新增待确认事项 |
| [CONTRACT_REVIEW.md](CONTRACT_REVIEW.md) | Q01—Q07：已发现问题、建议、需谁确认 |
| [artifact-access.md](artifact-access.md) | URI 读取提议与可执行演示 |
| [PAIRING.md](PAIRING.md) | 下一步沟通文字、三轮议程与空白决定表 |
| [ADR.md](ADR.md)、[Backlog.md](Backlog.md) | 本地决定/跨组提议和有负责人的任务 |
| [STATUS.md](STATUS.md)、[evidence/](evidence/) | 实际命令、通过/失败结果及边界 |
| [AI_USAGE.md](AI_USAGE.md)、[CONTRIBUTIONS.md](CONTRIBUTIONS.md)、[CHANGELOG.md](CHANGELOG.md) | AI 辅助、来源归属、贡献与版本记录 |

A11 自己的过程记录也包含在快照中，是来源证据；B11 状态以本目录文件为准。

## 运行

以下命令均在仓库根目录执行。当前 WSL 已准备好 `.venv`，可以直接运行验证。新机器需要 Python 3.10+：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r e2/requirements.txt
```

若当前 Debian/Ubuntu 环境缺 ensurepip 且已有系统 pip，可使用本次实际采用的隔离安装方式（以下路径适用于 Python 3.10）：

```bash
python3 -m venv --without-pip .venv
python3 -m pip install --target .venv/lib/python3.10/site-packages pip==25.2
.venv/bin/python -m pip install -r e2/requirements.txt
```

严格审阅未修改的 A11 原件：

```bash
.venv/bin/python e2/validate.py
```

当前会明确报告增量查询缺字段并退出 **1**。这条命令保留原件问题，供与 A11 讨论。

显式验证 B11 的待确认提议及本地读取准备：

```bash
.venv/bin/python e2/validate.py --proposed
```

当前退出 **0**，运行来源完整性、原 A11 校验、分类型输入、17 个回归检查和演示文件读取。不会联系外部服务或运行论文工具。

单独查看文件读取：

```bash
python3 e2/artifact_access.py --root fixtures/e2-handoff/artifacts --metadata fixtures/e2-handoff/artifact.json
```
