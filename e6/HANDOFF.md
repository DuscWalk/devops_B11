# E6 下一步：组员交接

更新：2026-11-03。下面是沿用 E2 模块分工的组内收尾安排，不是声称课件要求三人各跑一遍。

**孙静怡审阅 DRAFT；王硕已有 E6 成果，只补报告说明；胡博接收、核验、整合后提交。现在不需要重写实现，也不需要等 A11。**

## 已有什么

| 分支 | 已有内容 | 当前状态 |
| --- | --- | --- |
| `feat/e6-submission` | 完整报告、课件、课程源码、本组新增测试、复现脚本；学院服务器已通过 25 项单测、两轮构建、同镜像禁网运行及门禁 | 技术版本 `4abf849a2816c4df03ec162dc6e250d25c09f444`；本交接文档在其后补入 |
| `feat/e6-auto-build` | 王硕把 E6 接入仓库根目录服务，增加学号镜像入口，提交独立运行及报告 | `d95fefab7e0e463e910bfe208abf6729de9e8753`；27 项文件摘要和课程 E6 证据校验通过，尚未合入提交分支 |

两处分支是同一 GitLab 仓库。前者的运行目录是 `e6/labs/B-draft/`，后者在仓库根目录集成服务；路径不同，不要把它们当作两份都必须重新开发的任务。王硕成果的只读核验见 [接收记录](validation/wang-reception-d95fefa.json)。

## 孙静怡：审阅 DRAFT，交回一份结论

按原分工，你负责 DRAFT。本轮实现及运行证据已经准备好，你需要检查它是否正确并接手后续维护。

1. 阅读 [报告](REPORT.md) 的“源码如何生成报告”“新增测试”和“2026-11-03 提交脚本实测”。对照 [autobuild.py](labs/B-draft/services/draft/draft/autobuild.py) 与 [新增测试](labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py)。
2. 运行下面的归档校验命令。它不需要 Docker，不重新下载或构建镜像。
3. 阅读王硕的 [报告](https://git.nju.edu.cn/devops_b11/devops-project-b11/-/blob/d95fefab7e0e463e910bfe208abf6729de9e8753/docs/e6/E6_B_241250110.md) 和 [服务接入改动](https://git.nju.edu.cn/devops_b11/devops-project-b11/-/commit/d95fefab7e0e463e910bfe208abf6729de9e8753)，核对 `auto-build` 子命令如何进入同一个自动构建流程。
4. 按 [审阅模板](REVIEW_TEMPLATE.md) 交回结论。说明三个问题：第一轮为何必须失败且分类为 `MISSING_MAKE`；第二轮镜像 ID 如何关联运行命令；新增测试防止什么问题。发现问题就列出文件和原因，不必为了留下提交而制造代码修改。

在 Linux/WSL 的本人目录中执行。任一命令失败先停止，保留错误，不把失败结果填成通过：

```bash
mkdir -p ~/241250112
review_dir=$(mktemp -d ~/241250112/e6-review-XXXXXXXX)
git clone --single-branch --branch feat/e6-submission \
  git@git.nju.edu.cn:devops_b11/devops-project-b11.git "$review_dir/repo"
cd "$review_dir/repo"
git rev-parse HEAD
python3 e6/scripts/verify_archive.py > "$review_dir/archive-check.json"
cat "$review_dir/archive-check.json"
```

**交回胡博：审阅的完整 SHA、`archive-check.json`、填写后的审阅模板。**直接交文件或文字即可；如果通过 Git 交回，另开自己的审阅分支，只提交自己的记录，按课程要求使用学号作者，不直接推 main 或覆盖公共分支。

无需再做一份 Docker 全流程。若审阅发现需要验证的问题，再按 [README](README.md) 在新目录运行并保存新日志。

## 王硕：已有运行通过，补三处报告说明

你已推送 `feat/e6-auto-build`，不用重做 E6。请在自己的分支更新 `docs/e6/E6_B_241250110.md`：

1. **说明代码来源。**核对发现 `autobuild.py`、`lab_cloud.py`、证据校验器及两个新增到仓库的测试文件，与课程包对应文件逐字节相同。说明它们是引入课程参考实现；你的工作包括接入原 CLI、学号镜像入口、fixture 适配、运行和报告，不把课程文件登记为自己从零编写。
2. **修正日志路径。**第 5 节写的是 `e6-tests.log`，实际提交为 `e6/evidence/wang-shuo-20261103/.e6-tests.log`。把引用改到实际文件即可，不需要移动原日志。该日志显示 25 个测试进度点及 `[100%]`，没有另存 pytest 退出码；如实说明已有记录范围，不补写历史退出码。组级另有 25 项测试及退出码完整证据，不要求因此重跑。
3. **修改重跑步骤。**第 7 节不要用 `rm -rf work/e6-own` 删除旧证据；从本人的实际克隆目录执行，每次使用新输出目录。可替换为下方命令。

以下在自己的 `feat/e6-auto-build` 克隆根目录执行，不在公共服务器上切换别人的目录。镜像按你报告的服务构建步骤准备好后：

```bash
mkdir -p work
run_dir=$(mktemp -d "$PWD/work/e6-own-XXXXXXXX")
python3 scripts/course.py e6 \
  --candidate e6/candidates/candidate-01.Dockerfile \
  --out "$run_dir" --build-timeout 1200
python3 scripts/verify_e6_b_evidence.py --run-dir "$run_dir/evidence"
```

以上是**报告中的重跑说明**，这次只需修正文档，不要求再次执行。保留报告中真实的历史执行路径和日期，新的操作说明应从读者自己的克隆目录开始。

**交回胡博：更新后的分支和完整提交 SHA。**不要改原始日志或摘要，不需要另加一套测试。你已经完成的 E6 工作会按真实贡献接收。

## 胡博：接收与整合

1. 收孙静怡的模块审阅结论；检查王硕的报告修订，保留他的原始提交历史和运行证据。
2. 在整合分支接入王硕的根目录服务，明确最终推荐入口；检查这次 fixture 变更对原 E4 冒烟行为的影响。已有单测数量不能直接跨两套目录相加。
3. 更新组级报告、来源与贡献；核验合并后的内容。归档检查与实际 Docker 运行分开记录，不把原证据误写为合并后重新运行。
4. 核对课程学号作者要求与最终版本标识。现有 `4abf849` 作者为 `duscwalk`，不得把报告里的学号说明写成已经改变 Git 作者，也不改写他人的历史。
5. 经胡博明确授权再合并推送 main，按最终 SHA 重新打包交 LMS。

现在的 `B11-E6-20261103-review.zip` 固定在 `4abf849`，仍可用于审阅，**未包含刚发现的王硕 E6 分支和后续交接记录**。收齐并整合后生成新的提交包，不覆盖旧包。

## 可直接转发

> E6 的技术流程已跑通，现在做组内收尾。孙静怡请按 HANDOFF 的 DRAFT 审阅步骤检查代码和证据，交回 SHA、校验结果和简短审阅结论，不用重新写实现或完整重跑。王硕的 feat/e6-auto-build 已看到，E6 证据校验通过；请按 HANDOFF 补代码来源、测试日志路径和保留旧证据的重跑说明，更新分支后发 SHA。胡博负责接收、整合和最终提交。无需等 A11。
