# B11 E6 实验报告：候选自动构建与运行验证

整理日期：2026-11-03，更新：2026-11-04（America/New_York）。小组 B11，B 轨道 DRAFT。主运行及提交脚本实测归属胡博 241276007，Codex 辅助；另接收王硕 241250110 的根目录服务集成及独立运行，分别记录如下。仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11 。提交分支：`feat/e6-submission`，完整 SHA 记录于提交 ZIP 的 `MANIFEST.json`；已有审阅附件的版本范围见 [提交说明](SUBMISSION.md)。

## 任务与环境

按课件第 11–18 页，把 E5 保存的 Dockerfile 候选交给 CLI，自动执行初始构建、候选构建、同一镜像 ID 的程序运行，保存结构化报告和原始日志；新增至少一项测试，重新构建并运行门禁，说明源码和结果字段的对应关系。

原始运行于 2026-10-29 在学院华为云服务器完成，Ubuntu 22.04.5、x86_64、2 CPU、约 1.7 GiB 可见内存，Docker 29.1.3、Compose 2.40.3、Buildx 0.30.1。命令以 `duscwalk` 运行。课程 doctor 因通用 4 GiB 内存门槛返回 1，原始记录保留；后续实际运行成功。具体版本见 [doctor.txt](evidence/hu-bo-20261029/doctor.txt)。

本次代码来自课程 ZIP 的 B 轨道。31 个课程文件逐字节保留；本组贡献是新增候选约束测试、镜像源适配、复现脚本和实验材料。课程已经提供 `autobuild.py`，不登记为本组从零实现。来源和代码改动见 [来源与贡献](SOURCES_AND_CONTRIBUTIONS.md)。

## 输入、候选和自动流程

输入为课程 Tiny Greeting C 样例：Makefile 编译 `main.c`，程序输出 `hello E3\n`。初始 Dockerfile 使用 Python slim 镜像，保留 `WORKDIR /work`、`COPY main.c Makefile ./`、`RUN make` 和 `CMD ["./hello"]`，缺少构建工具。

E5 根据真实失败日志生成错误驱动和上下文驱动两类提示，Codex 分别返回候选。E6 读取已保存的上下文候选，增加 `build-essential` 和已验证的华为 HTTPS 源，保留项目、构建与运行指令。候选原始回复、来源、选择理由及提示均保留，见 [证据索引](EVIDENCE.md)。本次调用 CLI 时没有再次调用模型。

基础镜像固定为 `python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f`。候选摘要为 `6c1408e3365a8effc32df5321e54dbb6cd26bd89ee958d9c0f9009d4d17c70d1`。

以 [原始 E6 result.json](evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/result.json) 为例：

| 步骤 | 记录和结果 |
| --- | --- |
| 候选检查 | 固定 FROM 摘要，单阶段，原指令完整且顺序保持，新增 RUN 安装依赖 |
| 第一轮 | `build_exit_code=1`，实际日志含 `/bin/sh: 1: make: not found`，`failure_class=MISSING_MAKE` |
| 第二轮 | `build_exit_code=0`，保存 Dockerfile、构建日志及镜像 inspect |
| 镜像 | `sha256:c4b18f854cfa7b82029ef41340458a4aaa43ef9a3dfc5782e918040ebf99ffba` |
| 验证 | 运行命令使用上述完整 ID，`--network none --cpus 1 --memory 128m --pids-limit 64` |
| 输出 | `exit_code=0`，`actual_output="hello E3\n"`，`output_matches=true` |
| 总结论 | `status=SUCCEEDED`；课程证据校验器通过；输入与候选摘要通过 |

两轮只在独立的 `work/` 副本运行，原 fixtures 保持不变。候选镜像和服务镜像是两个不同对象：前者运行 C 程序，后者运行 Python CLI 并通过宿主机 Docker socket 驱动构建。

## 源码如何生成报告

实现位于 [autobuild.py](labs/B-draft/services/draft/draft/autobuild.py)，下列行号对应本次原样提取的课程源码。

| 函数/行号 | 对应行为和报告字段 |
| --- | --- |
| `prepare_candidate()`，27–47 行 | 验证固定 FROM、仅一个构建阶段和原项目/构建/运行指令，生成初始 Dockerfile |
| `classify_failure()`，61–66 行 | 将真实 shell 缺 make 日志分类为 `MISSING_MAKE`；网络错误另归 `INFRASTRUCTURE` |
| `auto_build()`，92–95 行 | 复制输入，逐文件计算 `input_sha256`，排除参考答案与工作目录 |
| 96–114 行 | 执行两轮构建，写 `attempts[].build_exit_code`；首轮未达到缺 make 或候选构建失败时停止 |
| 115–123 行 | inspect 第二轮镜像，把 `image_id` 同时用于结果记录和 `docker run`；禁网并限制资源 |
| 124–129 行 | 记录 `actual_output`、`exit_code`、`output_matches`，只有运行成功且输出匹配才设 `SUCCEEDED` |
| 130–143 行 | 区分失败/超时，清理容器，保存最终 `result.json` |

例如，`attempts[1].image_id` 并非由用户填写：第 119 行从实际 `image-inspect.json` 读取，第 122 行将相同变量放进运行命令。课程校验器会比较 inspect、报告和运行命令三个位置；本组归档核验还检查输出字节恰为 `hello E3\n`。课程实现的 `output_matches` 使用 `rstrip("\r\n")`，因此其通用判定允许末尾换行差异，不能把实现描述成严格字节比较。

## 新增测试、重新构建与运行

新增 [test_candidate_policy.py](labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py)。测试在一个原本合规的候选后追加 `FROM scratch AS extra-stage`，断言 `prepare_candidate()` 抛出 `Only single-stage candidates are supported`。它针对后续阶段绕过原项目构建与运行约束的情况，检验第 33–34 行的阶段数量约束。

增加测试后在云端重新构建服务镜像，原始日志见 [构建](evidence/hu-bo-20261029/build-hubo-20261029-customtest/service-build.log) 和 [单测](evidence/hu-bo-20261029/build-hubo-20261029-customtest/unit-tests.log)：课程 24 项加本组 1 项，共 **25 passed**。

按第 16 页要求，重新构建后运行课程门禁：[结果](evidence/hu-bo-20261029/e7-hubo-20261029-customtest/gate/gate-result.json) 中单测、正常候选、输出不符、无效候选、构建失败、运行超时全部通过。历史目录名称含 `e7`，这是课程门禁工具的原输出名，保留原路径；用于证明 E6 新增测试后的执行，不代表本次交付包含 E7 CI。

## 2026-11-03 提交脚本实测

本次在独立云端目录 `/home/duscwalk/241276007/e6-b11-20261103-review/` 重新构建并执行提交中的脚本，以 `duscwalk` 运行。正式结果在 [e6-reproduce-hnZQQFyP](evidence/reproduction-20261103/e6-reproduce-hnZQQFyP/)：

- 服务构建、25 项单测、E6 驱动、课程证据校验器、门禁驱动的退出码均为 0。
- [E6 结果](evidence/reproduction-20261103/e6-reproduce-hnZQQFyP/e6/evidence/result.json)：第一轮 `MISSING_MAKE`、第二轮构建成功，同一镜像禁网运行输出 `hello E3\n`，退出 0。
- 本轮候选程序镜像：`sha256:a223c9c059fa2e219676511df468a87a99baf719439532bb458735b4bd093878`；服务镜像：`sha256:127883804fa40f79a81313518da7b9b3d7d37ffa20935329b222b1614a82791b`。
- [门禁结果](evidence/reproduction-20261103/e6-reproduce-hnZQQFyP/gate/gate/gate-result.json)：单测及五场景全部通过。
- [33 项执行源码摘要](evidence/reproduction-20261103/e6-reproduce-hnZQQFyP/executed-source-sha256.json) 与本次提交的课程源码、新增测试和复现脚本一致。447 个新采集文件从服务器取回后逐项核验。

调试过程保留：首轮 `e6-reproduce-JsXyYI9m` 将裸镜像 ID 传给构建用的 FROM，BuildKit 将其解析为仓库名，服务构建退出 1；这属于复现脚本错误，不是课程缺 make 基线。第二轮 `e6-reproduce-RcPdeGAN` 改用独有本地标签，镜像解析等待后完整通过，没有因时长截断。最终脚本改为直接生成仅增加镜像源设置的工作 Dockerfile，避免本地基础标签解析，再次完整通过。三轮的命令、时间、退出码和日志均保留。

## 王硕的服务集成与独立运行

`d95fefa` 将课程 E6 核心及测试接入仓库根目录的服务骨架，扩展 CLI 并提供学号镜像入口；于 `8d63bee` 合入本分支。来源和命令见 [王硕报告](../docs/e6/E6_B_241250110.md)，`1e3a101` 已补齐代码来源及保留旧证据的重跑说明，个人交接已完成。

[独立运行结果](evidence/wang-shuo-20261103/e6-own/evidence/result.json) 记录首轮 `MISSING_MAKE`、第二轮构建成功，并用同一镜像 `sha256:ad96eb4df72181ea9a9946bd73f8b2478c93f90977036b90c4659390bd0aceb9` 禁网运行，退出 0、输出 `hello E3\n`。27 项证据摘要及课程校验器通过。个人服务单测日志只有 25 个进度点和 `[100%]`，未单独归档 pytest 退出码；上述组级 25 项单测与新增测试以各自完整记录为依据，两套数量不相加。

这里的记录是王硕原运行和归档核验，未登记为合并后的新 Docker 运行；孙静怡的模块审阅仍待交回。

## 复现、限制与证据

复现入口为 `bash e6/scripts/reproduce.sh`，完整说明见 [README](README.md)。它为每次运行生成新目录和独有镜像标签，从课程 Dockerfile 生成仅增加华为 HTTPS / PyPI 镜像源设置的工作副本；保存生成配方和摘要，不改课程原 Dockerfile、固定基础摘要和依赖哈希。下载故障与目标故障分开判断。E6 构建预算沿用课程 600 秒。

原始归档的 212 个文件均与原提交 `93b44511a7e23044edc215e85a0f9adbbb932e4f` 相同。迁移后的路径映射另存 [证据索引](EVIDENCE.md)，未修改历史日志中的云端绝对路径或候选来源记录。

本次仅覆盖课程 `hello E3` 微型样例和对应测试；没有进行论文数据集实验，也没有实现自动在线模型迭代。课件未要求 A11 的服务参与 B 轨道本次验收。成员贡献只登记已存在的实际工作，不将 E5 的独立复跑登记为新增 E6 执行。
