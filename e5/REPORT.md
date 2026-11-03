# B11 E5 实验报告：DRAFT 单次流程复现

整理日期：2026-11-02（America/New_York）。小组 B11，B 轨道 DRAFT。组员：胡博 241276007、孙静怡 241250112、王硕 241250110。本次主运行来自孙静怡的独立目录，另接收王硕的独立复跑和交叉核对；胡博授权接收分支、核验和汇总，具体贡献见 [CONTRIBUTIONS.md](CONTRIBUTIONS.md)。

仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11 。提交标签：`e5-b11-submission-20261102-r2`；完整提交 SHA 见交付附件 `MANIFEST.json`，也可运行 `git rev-parse e5-b11-submission-20261102-r2^{commit}`。原始贡献提交为 `3e6573ab13dd51f6dd101113c045c0285093eae8`。本报告按 [E5 课件](../docs/e5/E5_逐页文字.md) 第 17、19、20 页组织。

## 环境、输入与来源

学院华为云主机运行 Ubuntu 22.04.5，2 CPU、约 1.7 GiB 可见内存、Docker 29.1.3。运行目录为 `/home/duscwalk/241250112/e5-20261102`，使用普通系统账户。原始 [doctor](evidence/sun-jingyi-20261102/preflight/doctor.log) 因通用 4 GiB 内存检查返回 1；本次在学院分配的 2 GB 主机上实际完成后续构建和运行，资源自检失败原样保留。

输入为课程 Tiny Greeting C 项目，Makefile 执行 `cc main.c -o hello`，程序运行 `./hello`，预期 stdout 为 `hello E3\n`。输入副本见 [project](evidence/sun-jingyi-20261102/e5-01/project/)。这是课堂微型样例，论文项目扩展属于提高项。

所用脚本和 fixture 来自原始学生 ZIP，SHA-256 为 `4068d3bf98dc8218cc80c6a0f09674d9ed54289b3fcac5cb86eda327fb0cd688`；[源码清单](evidence/sun-jingyi-20261102/source/manifest.json) 中的文件与包内对应文件逐字节相同。教师提供脚本，组员没有将其登记为从零编写的实现。

## E5 结果与证据

以下路径均相对本文件；主运行证据位于 `evidence/sun-jingyi-20261102/`。

| 步骤 | 实际结果 | 原始证据 |
| --- | --- | --- |
| 初始构建 | Docker build=1；`RUN make` 内缺 make，退出 127；E5 驱动完成采集后退出 0 | [构建日志](evidence/sun-jingyi-20261102/e5-01/iter-01/build/stderr.log)、[结果](evidence/sun-jingyi-20261102/e5-01/iter-01/result-retry.json)、[驱动退出码](evidence/sun-jingyi-20261102/e5-driver-exit-code.txt) |
| 定位与提示 | 从本次日志抽取错误；保存错误驱动与增加 README 上下文的两类提示 | [错误定位](evidence/sun-jingyi-20261102/e5-01/iter-01/error-localization.json)、[错误提示](evidence/sun-jingyi-20261102/candidates/error-driven/prompt.txt)、[上下文提示](evidence/sun-jingyi-20261102/candidates/context-driven/prompt.txt) |
| 候选与选择 | 同会话 Codex 为两类提示各生成一份候选；先选择安装 `build-essential` 的上下文候选 | [错误候选来源](evidence/sun-jingyi-20261102/candidates/error-driven/provenance.json)、[上下文候选来源](evidence/sun-jingyi-20261102/candidates/context-driven/provenance.json)、[选择记录](evidence/sun-jingyi-20261102/selection.json) |
| 网络故障 | 默认 Debian HTTP 源下载停滞，首次构建主动中止，exit=130；不计为成功 | [中止说明](evidence/sun-jingyi-20261102/candidate-build-01/abort-note.json)、[原始日志](evidence/sun-jingyi-20261102/candidate-build-01/stderr.log) |
| 候选构建 | 后续将下载源改为华为 HTTPS；保留基础镜像 digest、项目和运行指令；88.75 秒、exit=0 | [最终候选](evidence/sun-jingyi-20261102/candidates/context-driven-mirror/Dockerfile)、[调整来源](evidence/sun-jingyi-20261102/candidates/context-driven-mirror/provenance.json)、[构建日志](evidence/sun-jingyi-20261102/candidate-build-02/stderr.log)、[退出码](evidence/sun-jingyi-20261102/candidate-build-02/result.json) |
| 程序验证 | 按成功构建的完整镜像 ID 禁网运行，exit=0，stdout 精确为 `hello E3\n`，容器已删除 | [运行命令](evidence/sun-jingyi-20261102/verification/command.json)、[结果](evidence/sun-jingyi-20261102/verification/result.json)、[stdout](evidence/sun-jingyi-20261102/verification/verify.log)、[清理](evidence/sun-jingyi-20261102/verification/cleanup-check.json) |

最终 image ID 为 `sha256:57dfd1ba5f0438ef068a2f42f0d0a315f32cf02e040be68d21de5b4b9ee2eeca`。构建导出的镜像、inspect、运行命令和结果记录一致。镜像仅在服务器 Docker daemon 中，未发布 registry；共享基础层可能命中缓存。实际工具链版本见 [toolchain.txt](evidence/sun-jingyi-20261102/verification/toolchain.txt)。

## 模型来源和论文对照

模型平台为 OpenAI Codex，精确服务端模型版本未记录；生成日期和提示/回复路径在各自 provenance 中。两份候选均由同一会话生成，没有独立 API 调用或 DeepSeek 新调用。每份 `model-response.txt` 的 Dockerfile 代码块与对应候选正文一致；后续换源改动单独保存 [adjustment.diff](evidence/sun-jingyi-20261102/candidates/context-driven-mirror/adjustment.diff)，未回写原始回复。

本次对应论文的“构建失败 → 错误/上下文提示 → 修复候选 → 选择 → 构建与功能验证”。按课堂提示脚本保存每类一份候选，并记录选择理由；未实现论文每轮三个候选的自动选择算法。错误驱动候选保留用于对照，没有声称它已经构建通过。仅完成 `hello E3` 样例，不以论文总体成功率或耗时作为本组结果。

## 王硕的独立复跑与交叉检查

王硕的运行记录见 [个人报告](WANG_SHUO_REPORT.md) 和 [原始证据](evidence/wang-shuo-20261102/)。运行源码为 GitHub `ff447978ba0ffb2f12e6cc45616e174a3d6faeb2`，使用组内 2026-10-29 已保存的候选；他根据本次失败重新生成提示，但没有将这些回放候选登记为本次新模型回复。与孙静怡的基础 digest、缺 make 失败和输出结论一致，候选指令顺序与下载源不同，分别保留运行结果。

正式补充记录 `candidate-build-02` 构建退出 0，日志中的镜像 ID 与 `image-id.txt` 一致；`verify-02` 记录退出 0、stdout 精确为 `hello E3\n`、stderr 为空。镜像 ID 为 `sha256:49dc498ec1cb1984f45c54ddd167d27825f4d892fb8f6e108485206f2b47ed6d`。王硕个人报告说明运行了该镜像；归档中的运行命令仍为 `<image-id>` 占位，未另存包含实际 ID 的命令记录。本次按组长确认保留现状，不将这点写成新增的机器核验通过项。

两名成员的归档摘要均通过；王硕目录的 63 项摘要覆盖除清单自身以外的全部文件。[接收核验](evidence/submission-20261102/wang-shuo-audit.json) 记录核对范围。原 `e5-01/e5-console.log` 只含服务构建 `work/build-01` 的目录输出，现移至 [build-01/build-console.log](evidence/wang-shuo-20261102/build-01/build-console.log)，内容未改。其额外 26 项服务单测记录作为补充材料保留，不作为 E5 额外要求。

## 接收与复现

胡博本次授权接收成员分支。提交整合核验了原始证据摘要、课程源码来源、提示生成结果、原始模型回复、候选摘要、构建退出码、镜像 ID 和输出；详见 [接收核验](evidence/submission-20261102/audit.json)。本次接收核验没有重新运行 Docker，主运行结果仍明确归属于上述成员记录，未登记成员新增人工签字。

本次 r2 标签和附件纳入两名成员成果，旧标签 `e5-b11-submission-20261102` 继续指向首次汇总版本，不移动或覆盖。

完整重现命令见 [README](README.md#复现-e5)；无需 API Key，可回放已保存候选。独立复现应写入新目录并保留自己的日志。原始个人报告保留其提交时的交接状态，当前组级接收状态以本报告为准。

E6 自动构建服务、E7 单元/故障测试和 GitHub CI 属于后续实验；本次验收和提交只包含 E5。已有后续成果不计入本报告的 E5 完成依据。
