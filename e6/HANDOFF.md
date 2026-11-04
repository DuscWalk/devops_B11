# E6 下一步：组员交接

更新：2026-11-04。下面是沿用 E2 模块分工的组内收尾安排，不是声称课件要求三人各跑一遍。

**王硕的 E6 实现、运行和报告交接已完成；孙静怡的 DRAFT 审阅待交回；胡博负责最终核验与提交。现在不需要重写实现，也不需要等 A11。**

## 已有什么

| 分支 | 已有内容 | 当前状态 |
| --- | --- | --- |
| `feat/e6-submission` | 完整报告、课件、课程源码、本组新增测试、复现脚本；学院服务器已通过 25 项单测、两轮构建、同镜像禁网运行及门禁；另接收王硕根目录服务与证据 | 基础技术版本 `4abf849`；`8d63bee` 接收王硕分支，`1e3a101` 补齐其来源及重跑说明；当前审阅以拉取后的完整 SHA 为准 |
| `feat/e6-auto-build` | 王硕把 E6 接入仓库根目录服务，增加学号镜像入口，提交独立运行及报告 | `d95fefab7e0e463e910bfe208abf6729de9e8753`；27 项文件摘要和课程 E6 证据校验通过；已于 2026-11-04 合入 `feat/e6-submission`（合并提交 `8d63bee`） |

两处分支是同一 GitLab 仓库。前者的运行目录是 `e6/labs/B-draft/`，后者在仓库根目录集成服务；路径不同，不要把它们当作两份都必须重新开发的任务。王硕成果的只读核验见 [接收记录](validation/wang-reception-d95fefa.json)。

## 孙静怡：审阅 DRAFT，交回一份结论

按原分工，你负责 DRAFT。本轮实现及运行证据已经准备好，你需要检查它是否正确并接手后续维护。

1. 阅读 [报告](REPORT.md) 的“源码如何生成报告”“新增测试”和“2026-11-03 提交脚本实测”。对照 [autobuild.py](labs/B-draft/services/draft/draft/autobuild.py) 与 [新增测试](labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py)。
2. 运行下面的归档校验命令。它不需要 Docker，不重新下载或构建镜像。
3. 阅读王硕的 [当前报告](../docs/e6/E6_B_241250110.md) 和 [服务接入改动](https://git.nju.edu.cn/devops_b11/devops-project-b11/-/commit/d95fefab7e0e463e910bfe208abf6729de9e8753)，核对 `auto-build` 子命令如何进入同一个自动构建流程。
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

## 王硕：已完成，无需补交

- 实现、独立 E6 运行及原始证据已合入本分支；27 项摘要和课程证据校验通过。
- `26ff16f` 已统一日志路径；`1e3a101` 已补明课程代码来源，并改为新目录重跑、保留旧证据。
- 胡博本次授权完成文档排版、记录范围及状态同步。个人测试日志没有独立退出码的事实保留，不补造数据，也不要求因此重跑。

当前报告见 [E6_B_241250110.md](../docs/e6/E6_B_241250110.md)。王硕无需再重复开发、运行或补交同一项材料。

## 胡博：接收与整合

1. 收孙静怡的模块审阅结论；王硕的报告修订已接收，原始提交历史和运行证据保留。
2. 王硕的根目录服务已合入本分支。最终核验时检查 fixture 变更对原 E4 冒烟行为的影响；完整 E6 复现推荐使用 [README](README.md) 的 `bash e6/scripts/reproduce.sh`。已有单测数量不能直接跨两套目录相加。
3. 更新组级报告、来源与贡献；核验合并后的内容。归档检查与实际 Docker 运行分开记录，不把原证据误写为合并后重新运行。
4. 核对课程学号作者要求与最终版本标识。现有 `4abf849` 作者为 `duscwalk`，不得把报告里的学号说明写成已经改变 Git 作者，也不改写他人的历史。
5. 经胡博明确授权再合并推送 main，按最终 SHA 重新打包交 LMS。

旧的 `B11-E6-20261103-review.zip` 固定在 `4abf849`。仓库内的 [B11-E6-20261104-review.zip](attachment/B11-E6-20261104-review.zip) 固定在 `1e3a1012f9b82c9f89472324e47891dcb82a16ad`，包含王硕分支及其报告修订，未包含本次文档收尾。两份都是对应 SHA 的审阅快照；最终提交前按最终 SHA 重新打包。

## 可直接转发

> 王硕的 E6 工作及报告交接已完成，无需再补交。孙静怡请按 HANDOFF 审阅 DRAFT，交回 SHA、归档校验结果和简短结论，不用重新开发或完整重跑。胡博负责最终核验、合并与提交，无需等 A11。
