# E6 证据索引与迁移说明

原始归档来自提交 `93b44511a7e23044edc215e85a0f9adbbb932e4f` 的 `e5/evidence/hu-bo-20261029/`，本次选择 212 个相关文件移入 [evidence/hu-bo-20261029/](evidence/hu-bo-20261029/)。文件逐字节不变，全部与原历史提交核对；新选择清单为 [SHA256SUMS.json](evidence/hu-bo-20261029/SHA256SUMS.json)。

| 内容 | 当前路径（均在上述归档根目录下） |
| --- | --- |
| 环境自检及失败退出码 | `doctor.txt`、`doctor-exit-code.txt` |
| 服务镜像源适配层 | `service-base-mirror.Dockerfile` |
| E5 失败、提示和手工候选构建/运行 | `e5-02/`，其中两类提示在 `iter-01/` |
| 两类候选、模型原始回复与来源 | `candidate/` |
| E6 主运行 | `e6-hubo-20261029-mirror/`：调用、runner 退出码，以及 `evidence/` 下的两轮构建、输入、哈希和程序验证 |
| 原服务构建与官方源诊断 | `build-hubo-20261029/`；未通过的网络尝试仅用于解释问题 |
| 新增测试后的服务构建 | `build-hubo-20261029-customtest/`：构建日志、镜像 inspect 和 25 项单测 |
| 新增测试后的门禁执行 | `e7-hubo-20261029-customtest/`：单测和五场景原始证据 |

候选 `provenance.json` 保留了原运行目录中的相对路径，按以下映射查找，不改写原始来源记录：

- `work/candidate/...` → 本次归档 `candidate/...`。
- `evidence/hu-bo-20261029/e5-02/...` → 本次归档 `e5-02/...`。
- 日志中的 `/home/duscwalk/241276007/e5-b11-20261029/...` 是实际历史云端路径。
- 容器中的 `/evidence/` 是每次运行映射进去的证据目录；`result.json` 中的容器内路径不是提交包缺失文件。

输入的原始 Dockerfile 在 `e6-hubo-20261029-mirror/evidence/project/Dockerfile.broken`，两轮实际 Dockerfile 在 `iter-01/Dockerfile` 与 `iter-02/Dockerfile`。两者之间的可读 diff 见 [candidate-repair.diff](candidate-repair.diff)。

服务镜像 ID 与候选程序镜像 ID 应分别解释；不要把服务 build 日志中的 ID 当作被验证的 C 程序镜像。E6 程序镜像的 inspect、报告和运行命令由课程校验器交叉核对。

## 王硕 241250110 的服务集成证据

[wang-shuo-20261103](evidence/wang-shuo-20261103/) 保存王硕在仓库根目录接入 `auto-build` 的完整运行记录：28 个文件、13 份原始日志（`build-service-image.log`、`service-tests.log`，以及 `e6-own/evidence/` 下两轮构建、镜像检查、禁网验证、清理与 runner 的 stdout/stderr）。

| 内容 | 结果 |
| --- | --- |
| 第一轮（初始 Dockerfile） | 退出 1，`MISSING_MAKE`，日志含 `make: not found` |
| 第二轮（候选） | 退出 0，镜像 `sha256:ad96eb4df721…0aceb9` |
| 断网运行 | 同一镜像 ID、`--network none`，退出 0，stdout 精确 `hello E3` |
| 课程校验器 | `passed: true`，trace `e6-b-a2b1782bd9594814921af948843dc0f1` |
| 服务单测 | 25 passed |

根目录 `SHA256SUMS.txt` 覆盖其余 27 个文件，日志重命名后已重算并逐条通过。

## 本次复现脚本验证

[reproduction-20261103](evidence/reproduction-20261103/) 保存本次新增脚本的三轮云端记录，详细元数据见 [reproduction.json](reproduction.json)。

| 目录 | 结果 |
| --- | --- |
| `e6-reproduce-JsXyYI9m/` | 服务构建错误：裸镜像 ID 被当作仓库名解析；退出 1，未进入 E6 |
| `e6-reproduce-RcPdeGAN/` | 使用独有本地基础标签，构建、25 项单测、E6 和门禁通过 |
| `e6-reproduce-hnZQQFyP/` | 当前提交脚本：仅在工作 Dockerfile 插入镜像源设置；全流程通过，是本次正式复现结果 |

本轮 [SHA256SUMS.json](evidence/reproduction-20261103/SHA256SUMS.json) 在服务器计算，下载后校验，共 447 个文件。最终目录还保存 `executed-source-sha256.json`，对应执行时的 31 个课程文件、1 项自定义测试及复现脚本；`build-source.json` 记录课程、适配层和生成 Dockerfile 的摘要。所有 `.log` 均纳入 Git。
