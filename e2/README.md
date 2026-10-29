# B11 E2 提交材料

| 项目 | 内容 |
| --- | --- |
| 小组 / 配对组 | B11 / A11 |
| 分工 | B11：DRAFT、MDFixer、公共接口与联调 |
| 仓库 | https://git.nju.edu.cn/devops_b11/devops-project-b11 |
| 协议 / 提交修订 | schema_version 1.1.0 / b11-e2-r1 |
| 确认 | 2026-09-22 确认 A11 已认可，见 AGREEMENT.md |
| 验证入口 | 仓库根目录 `.venv/bin/python e2/validate.py` |

## 交付索引

| 课程要求 | 文件 |
| --- | --- |
| 统一任务模型 | [task.schema.json](task.schema.json)、[contract.py](contract.py)（跨字段检查） |
| 四类请求、202、查询、错误与发现样例 | [contract-examples.json](contract-examples.json) |
| 四个创建接口与查询 | [openapi.yaml](openapi.yaml)（E2 约定，未部署） |
| DRAFT 交接 | [请求与响应](../draft/examples/)、[产物文件](../fixtures/draft-handoff/README.md) |
| MDFixer 交接 | [请求/响应/人工报告](../mdfixer/examples/)、[源码与来源](../fixtures/mdfixer-project/README.md)、[真实本地结果](evidence/mdfixer-2026-09-22/result.json) |
| 产物读取 | [artifact-access.md](artifact-access.md)、[artifact_access.py](artifact_access.py) |
| 配对确认与三轮内容 | [AGREEMENT.md](AGREEMENT.md)、[PAIRING.md](PAIRING.md) |
| 设计与任务 | [ADR.md](ADR.md)、[Backlog.md](Backlog.md)、[CONTRACT_REVIEW.md](CONTRACT_REVIEW.md) |
| AI / 个人贡献 / 变更 | [AI_USAGE.md](AI_USAGE.md)、[CONTRIBUTIONS.md](CONTRIBUTIONS.md)、[CHANGELOG.md](CHANGELOG.md) |
| 实际完成与失败记录 | [STATUS.md](STATUS.md)、[evidence/](evidence/) |
| LMS 与提交版本 | [SUBMISSION.md](SUBMISSION.md) |

## 运行与预期

当前 WSL 已有虚拟环境。新机器从仓库根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r e2/requirements.txt
.venv/bin/python e2/validate.py
```

Linux/WSL 还需要 Git、Make、C 编译器。若系统没有 ensurepip 但有系统 pip（本机 Python 3.10 实际使用的方式）：

```bash
python3 -m venv --without-pip .venv
python3 -m pip install --target .venv/lib/python3.10/site-packages pip==25.2
.venv/bin/python -m pip install -r e2/requirements.txt
```

预期整体退出 0：4 类请求、202、4 个查询、3 个完整失败 Job、6 个非法样例；20 个公共契约/读取回归、6 个 MDFixer 回归；DRAFT/MDFixer 专有样例；8 个产物文件的真实摘要；一次本地补丁构建验证。非法 ABC job_type 和缺 baseline 必须拒绝。详细结果见 STATUS。

`--proposed` 保留为旧命令别名，默认已使用正式提交版；`--reference` 仅运行旧 A11 42 项校验，不能替代正式入口。ZIP 解压后也可验证，DRAFT 不再依赖归档之外的 Git 对象，MDFixer 源码提交包含在 project.bundle。

## 来源与执行边界

A11 原始 96f35cc 快照在 [reference/](reference/README.md) 原样保留。最新 8b0c3b9 的四份契约核心文件与旧快照一致，见来源核对记录。正式提交版在 e2 根目录修复已发现的字段和校验遗漏，没有改写 A11 仓库。

`contract-examples.json` 是教学报文，不能当作真实检测结果；DRAFT 成功样例标记 example_only。MDFixer 示例响应来自本次人工小项目的实际本地运行，报告明确 MANUAL，未调用 A11 检测器。各历史审阅/失败证据仍保留当时状态，以 STATUS 和 AGREEMENT 为当前结论。
