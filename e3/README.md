# B11 · E3 并行测试基线

小组 B11；配对 A11。孙静怡负责 DRAFT，王硕负责 MDFixer，胡博负责公共验收、证据整合和配对交接。完整课件和要求见 [docs](../docs/README.md)。E2 契约与历史证据保留在 `e2/`。

2026-10-12：公共基线与 DRAFT 材料保留；胡博已修复 MDFixer 分支，完成本轮运行归档；组员人工交叉复核和正式提交仍待完成。三人已完成/未完成内容见 [状态](STATUS.md)、[任务表](Backlog.md)、[贡献](CONTRIBUTIONS.md)，各自下一步见 [交接](HANDOFF.md)。

## 一键运行

Linux/WSL，Python 3.10+、Git、GNU Make、C 编译器；沿用 E2 的虚拟环境。新机器先安装 `e2/requirements.txt`：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r e2/requirements.txt
.venv/bin/python e3/scripts/run_baseline.py
```

最后打印 `EVIDENCE_DIR=...`。每次生成新目录 `e3/work/<时间>-<随机标识>/`；禁止覆盖旧运行。工作副本、Git 初始化、clean、补丁和头文件修改只发生在该目录，不修改原模块或固定 fixture。

本入口完成：课件摘要核验、证据基础设施回归、E2 正式校验；Tiny Greeting 本地构建/行为；四种人工参考补丁；未修复旧值与 clean 对照；修复后不 clean 的头文件重建；真实失败候选的拒绝/恢复；现有 MDFixer 原型；新产物异目录读取与损坏摘要拒绝。四种人工参考仍独立验证；E2 入口中的 MDFixer 回归另外实际执行自动生成补丁的四风格构建测试，支持范围见 [模块记录](mdfixer-notes.md)。

## Docker 独立检查

Docker daemon 可用、可下载 `python:3.13-slim` 和 APT 包时运行：

```bash
.venv/bin/python e3/scripts/verify_docker.py
```

记录缺工具链的真实失败和参考成功，保留构建日志、镜像 ID、基础镜像摘要、包清单；断网容器重建并验证 `hello E3`。网络失败会返回失败并保留日志，不计入预期工具链故障。该命令不发布镜像；生成唯一的 `b11/e3-tiny-reference:<标识>` tag，容器运行后自动移除，镜像供后续查看。

## 导出和交接

```bash
.venv/bin/python e3/scripts/run_baseline.py --export-evidence e3/evidence/你的编号-新运行
```

导出日志、元数据、补丁与结果，排除 `work/` 中的构建产物和 `.git`。`--out` / `--export-evidence` 必须是未存在的目录。Docker 检查支持相同参数。已有归档见 [evidence/README](evidence/README.md)；先按 [HANDOFF](HANDOFF.md) 交给组员。

## 文件入口

| 内容 | 文件 |
| --- | --- |
| 任务、状态、成员贡献 | [Backlog](Backlog.md)、[STATUS](STATUS.md)、[CONTRIBUTIONS](CONTRIBUTIONS.md) |
| 组员交接和 A11 待确认项 | [HANDOFF](HANDOFF.md) |
| 人工样例、来源与原型支持范围 | [fixtures/README](fixtures/README.md) |
| 环境指纹提案、产物互读 | [environment-hash](environment-hash.md)、[artifact-access](artifact-access.md) |
| 决策、AI 使用、提交清单 | [ADR](ADR.md)、[AI_USAGE](AI_USAGE.md)、[SUBMISSION](SUBMISSION.md) |

E3 独立样本可验收；真实镜像接收、检测器报告与重检仍需后续实际联调。环境哈希为 `PROPOSED_B11_ONLY`，不改 E2 Schema，不把本地 GCC 11 写成 fzy 的 GCC 13 环境。
