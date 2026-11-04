# B11 E6：DRAFT 候选自动构建与验证

本目录按 [E6 课件](../docs/e6/README.md) 整理。输入为 E5 保存的候选 Dockerfile，CLI 自动确认 `MISSING_MAKE`，构建候选，再用产生的完整镜像 ID 禁网验证 `hello E3`。

入口：[实验报告](REPORT.md)、[要求核对](REQUIREMENTS_CHECK.md)、[来源与贡献](SOURCES_AND_CONTRIBUTIONS.md)、[证据索引](EVIDENCE.md)、[提交说明](SUBMISSION.md)。

**组员下一步见 [交接安排](HANDOFF.md)：孙静怡审阅 DRAFT；王硕的 E6 分支已于 2026-11-04 合入（`8d63bee`），个人报告见 [E6_B_241250110](../docs/e6/E6_B_241250110.md)；胡博接收与整合。**原分工继续沿用，已有运行无需三人重复一遍。

## 目录

| 路径 | 内容 |
| --- | --- |
| `labs/B-draft/` | 课程 B 轨道源码、锁文件、CLI、fixtures，以及 B11 新增的一项候选约束测试 |
| `evidence/hu-bo-20261029/` | 原始云端实验日志、两类候选/回复、两轮构建及重新构建后的单测和门禁 |
| `evidence/reproduction-20261103/` | 本次复现脚本的云端验证，最终成功目录为 `e6-reproduce-hnZQQFyP/`；保留前序诊断 |
| `evidence/wang-shuo-20261103/` | 王硕 241250110 的仓库根服务集成运行：两轮构建、镜像检查、断网验证、25 项单测与原始日志 |
| `scripts/reproduce.sh` | 使用已验证镜像源，在新目录构建服务并执行 E6、单测和门禁 |
| `scripts/verify_archive.py` | 不运行 Docker，核验课程来源、归档摘要和结果的一致性 |
| `source-manifest.json` | 课程文件逐项摘要、原提交和迁移路径 |

## 本地检查已有证据

从仓库根目录执行，需 Python 3.10+，无需安装依赖：

```bash
python3 e6/scripts/verify_archive.py
```

预期 `passed: true`。该命令检查已有记录，不把历史构建登记为新运行。

2026-11-03 已在学院服务器使用本次脚本重新构建并完整运行：25 项单测通过、E6 校验通过、五场景门禁通过。执行源码的 33 项摘要与本次提交一致，见 [复现元数据](reproduction.json)。

## 在学院云服务器重新运行

从仓库根目录执行以下命令。使用可访问本机 Docker daemon 的普通账户，依赖 Bash、Python 3.10+ 和 Docker；无需模型 API Key。

```bash
bash e6/scripts/reproduce.sh
```

脚本打印 `E6_RUN_DIR=...`，所有新日志写入 `e6/labs/B-draft/work/e6-reproduce-随机串/`。服务镜像采用本次独有的标签，服务启动使用实际镜像 ID。成功时打印 `E6_REPRODUCE=PASS`。具体记录包括：

1. `service.Dockerfile`、`build-source.json`、`service-build/`、`service-inspect/`：仅在工作副本增加华为 HTTPS / PyPI 镜像源设置并构建服务；保存生成配方和来源摘要，课程原 Dockerfile 与带哈希的依赖锁保持原内容。
2. `unit-tests/`：课程 24 项及 B11 新增 1 项，共 25 项通过。
3. `e6/evidence/`：两轮 Dockerfile、构建日志、输入哈希、image inspect、`result.json` 和 `verify.log`。
4. `e6-check/`：课程校验器结果，应为 `passed: true`。
5. `gate/gate/`：新增测试后运行的单元测试和五场景结果，应全部通过；这不包含 E7 的 CI 接入任务。

构建及各步骤的命令、开始/结束时间、退出码和 stdout/stderr 分别记录。查看正在构建的日志可使用 `tail -f` 加对应的 `stderr.log` 路径。

独立执行 E6 的课程命令如下。`<本次服务镜像ID>` 从脚本生成的 `service-inspect/stdout.log` 取得；每次必须更换输出目录名：

```bash
cd e6/labs/B-draft
python3 scripts/lab_cloud.py e6 \
  --image '<本次服务镜像ID>' \
  --candidate ../../evidence/hu-bo-20261029/candidate/Dockerfile \
  --out work/e6-own-01 --build-timeout 600
python3 scripts/verify_e6_b_evidence.py --run-dir work/e6-own-01/evidence
```

E6 使用课程给出的 600 秒构建预算。若日志显示拉取或下载失败，先排查网络和镜像源；这类错误不能作为 `MISSING_MAKE`。学院分配的 2 GB 主机已经完成本实验，历史 doctor 的通用 4 GiB 检查失败记录保留在归档中。
