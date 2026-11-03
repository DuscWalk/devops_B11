# 来源、改动和贡献

## 课程实现

原始学生包为 `docs/e5/E5-7_Student_Cloud.zip`，SHA-256：`4068d3bf98dc8218cc80c6a0f09674d9ed54289b3fcac5cb86eda327fb0cd688`。其中 B 轨道 31 个文件提取到 `e6/labs/B-draft/`，全部与 ZIP 内对应文件逐字节相同。只省略本次无须安装的 `.github/workflows/e7-quality-gate.yml`。课程 README、Makefile 保留原貌；本次操作以 [E6 README](README.md) 为准。

`autobuild.py`、`lab_cloud.py`、校验器和原有 24 项测试属于课程提供内容。`scripts/run_e7_b_gate.py` 是原包组成部分，课程原测试会导入其判定函数；E6 第 16 页也要求新增测试后运行门禁，因此保留。

## 本组改动

| 文件/材料 | 来源及用途 |
| --- | --- |
| `labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py` | 胡博授权 Codex 在 2026-10-29 增加，验证禁止追加第二个构建阶段；本次从原提交原样移入 |
| `evidence/hu-bo-20261029/service-base-mirror.Dockerfile` | 原云端网络适配层，切换 Debian HTTPS/PyPI 镜像源，保留课程镜像构建配方与依赖锁 |
| `scripts/reproduce.sh` | 本次整理新增，生成仅增加镜像源设置的工作 Dockerfile，选择独有目录和服务镜像标签，记录命令及退出码，串联构建、E6 校验和门禁 |
| `scripts/verify_archive.py` | 本次整理新增，核对课程原件、历史证据摘要、同一镜像 ID 和结果 |
| 报告、课件文字、来源清单、证据索引及提交包 | 本次按 E6 课件单独整理 |

原始实验及自定义测试来源提交为 `93b44511a7e23044edc215e85a0f9adbbb932e4f`。本次以 GitLab E5 提交 `2e9d3527494adbffbaf11503ae56137cd42c8bc5` 为基础，在独立分支增加 `e6/` 和 `docs/e6/`。E5 原报告、成员证据和固定提交标签保留。

## 成员和 AI 辅助范围

- 胡博（241276007）：原云端 E6 运行、新增测试、本次整理及 2026-11-03 新脚本的云端复现由本人授权 Codex 辅助完成；执行、日志整理和文档编辑不登记为纯手工操作。
- 孙静怡（241250112）：原 DRAFT 模块负责人，E5 贡献保留于 `e5/`；本轮模块审阅待交回，具体步骤见 [交接安排](HANDOFF.md)。
- 王硕（241250110）：新发现 GitLab 分支 `feat/e6-auto-build`，提交 `d95fefab7e0e463e910bfe208abf6729de9e8753`，将课程 E6 实现接入原服务、增加学号镜像入口，并提供独立 E6 运行与个人报告。27 项证据摘要和课程校验器通过，见 [只读接收核验](validation/wang-reception-d95fefa.json)。该分支尚未整合到本分支，不把只读核验登记为新增 Docker 运行或成员人工审阅。

历史候选由 OpenAI Codex 根据当时两类提示生成，精确后端版本未记录，来源文件原样保留。E6 CLI 回放已保存的候选，没有在线生成新模型答案。课件没有要求每位成员分别运行，也未把 A11 反馈列为 B 轨道 E6 前置条件。组内交接时应能解释第一轮为何预期失败、image ID 如何关联、以及新增测试检验什么。
