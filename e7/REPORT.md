# B11 E7 实验报告：验证与合并门禁

核验日期：2026-11-10（America/New_York）。小组 B11，B / DRAFT。仓库：https://github.com/DuscWalk/devops_B11 。本次审阅分支为 `review/e7-handoff`。

**整体状态：DRAFT 审阅待共享，CI 交叉验收与最终整合待完成。** 本报告中的通过结论对应已完成的技术检查和原始运行；孙静怡委托 Codex 的 [DRAFT 场景验收](reviews/241250112-DRAFT.md) 已形成，但尚未推送，CI 交叉验收及最终接收尚未完成，见 [状态](STATUS.md)。

## 技术核验和本次修改

E7 的核心能力、五个实际工作流场景、同一 PR 的失败拦截和修复合并已经执行。本次重新查询 GitHub，并下载正常、失败、恢复三次 artifact，分别与仓库中的 139、16、139 个文件逐字节一致；补存当前 main 的成功运行与保护配置。

本次将工作流从 `e5-b-quality-gate.yml` 更名为课件指定的 `e7-quality-gate.yml`，显示名称改为 E7，保持必需检查 `e7-b-quality-gate`。另外保存 `trigger.json`（PR head 与实际检出 SHA）及 `gate-exit-code.txt`，使触发版本和命令退出码更直接可查；补齐独立报告、课程材料、验收表和归档校验器。未改变 DRAFT 算法和场景预期。

## 环境、来源与测试

GitHub CI 使用 Ubuntu 24.04 托管 runner；Docker 版本和服务镜像 inspect 在各 artifact 中。此前云端 gate 在学院 2 GB 主机完成，原始 doctor 的通用 4 GiB 检查未通过，不能把该检查记成通过。这里的结论只覆盖课程 `hello E3` 微型样例，未做论文数据集基准实验。

核心实现及门禁来源为 [课程学生包](../docs/e5/E5-7_Student_Cloud.zip)，实际使用的实现位于 `e5/labs/B-draft/`。CI 使用该包保存的 [DeepSeek-E5 候选](../e5/labs/B-draft/fixtures/ci-candidates/DeepSeek-E5.Dockerfile)，没有在线模型/API 调用；它与 E6 云端记录中的本组候选分别归档。

测试数为课程 24 项 + [B11 多阶段候选拒绝测试](../e5/labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py) 1 项 + [合并拒绝演示的 version 测试](../e5/labs/B-draft/services/draft/tests/test_ci_reject_demo.py) 1 项，共 **26 项**。正常 PR #1 只有前 25 项；PR #2 添加第 26 项，先故意把成功退出码期望写成 1，再改回 0。此过程验证错误测试能阻断合并，属于修正预期，不是修正算法。多阶段测试用于拒绝在合法候选后追加构建阶段。

## 场景：先写预期，再核对实际

下表预期来自课程门禁实现和 E7 第 9–12 页；实际以当前 main `8e84e4215275ed8fab14de801bae1df910e87677` 的运行 [41558352072](https://github.com/DuscWalk/devops_B11/actions/runs/41558352072) 为例。对应 artifact 在 `e7/evidence/verification-20261110/main-artifact/e7-b-evidence-41558352072-1/`，场景目录均在其 `gate/` 下。

| 检查项/输入 | 预期 | 实际状态、退出码与判定 | 原始证据 |
| --- | --- | --- | --- |
| 服务单测 | 全部通过，exit 0 | 26 passed，exit 0，PASS | `unit-tests/stdout.log` |
| 正常候选 | 缺 make → 修复构建 → 同镜像禁网输出 | `SUCCEEDED` / 0，build `[1,0]`，run 0，`hello E3\n`，PASS | `success/evidence/result.json`、两轮构建、inspect、`verify.log` |
| 输出不符 | 故意预期其他文本，应拒绝 | `FAILED` / 1；程序仍 run 0、输出 hello E3，`output_matches=false`，PASS | `wrong-output/command.json`、`evidence/result.json` |
| 改变 CMD 的候选 | 构建前拒绝，无轮次 | `FAILED` / 1，未创建构建 project/iter，PASS | `invalid-candidate/stdout.log`、候选副本 |
| 第二轮注入 `RUN exit 23` | 第二轮失败，不运行程序 | `FAILED` / 1，build `[1,1]`，没有 verification，原日志记录 exit 23，PASS | `build-failed/evidence/iter-02/build-stderr.log` |
| 两个 Dockerfile 同时延迟 CMD | 构建成功，1 秒运行预算超时并清理 | `TIMED_OUT` / 1，build `[1,0]`，保存容器 ID，inspect 返回 No such container，PASS | `runtime-timeout/fault-injection.json`、`evidence/cleanup-check/` |

`results.csv` 与 `gate-result.json` 六项逐项一致、全部 `passed=true`。故障场景的工具 exit 1 是预期行为，整体 gate 因所有场景符合预期而 exit 0。第一轮必须有真实 `make: not found`；网络或下载失败不算目标故障。构建服务使用 bridge 网络，最终程序使用 `--network none`。

## 正常、失败、恢复和合并

| 阶段 | PR / run | PR head SHA | artifact 中实际检出 SHA | 结果 |
| --- | --- | --- | --- | --- |
| 正常 | [#1](https://github.com/DuscWalk/devops_B11/pull/1) / [40895134404](https://github.com/DuscWalk/devops_B11/actions/runs/40895134404) | `890bec83a84eef00f88ee418decabeae302cc66e` | `0e2d6f010385acb999c8cd6050a234e14924bebc` | 25 单测 + 五场景通过 |
| 故意失败 | [#2](https://github.com/DuscWalk/devops_B11/pull/2) / [40895904554](https://github.com/DuscWalk/devops_B11/actions/runs/40895904554) | `159139ce49e885bbca831b638c2dd9de51989894` | `741cebb23bc2a98739d5d75a43ef6b9c59d1066d` | `assert 0 == 1`，1 failed / 25 passed，CI failure |
| 同一 PR 修复 | [#2](https://github.com/DuscWalk/devops_B11/pull/2) / [40896410596](https://github.com/DuscWalk/devops_B11/actions/runs/40896410596) | `6b1028bcfc48551452c9a220a770e64c74011724` | `700f16b838eb437a219fc039e6b6149c8179685a` | 26 单测 + 五场景通过，CLEAN 后 MERGED |

PR workflow 默认检出 GitHub 生成的临时合并提交，所以 `commit.txt` 与 PR head 不同是正常行为。本次保存对应 Git commit API 返回，确认上述临时提交的父提交包含各自 PR head；没有把两个 SHA 混写成同一个。下载 artifact 原件仍保留原字节。

历史证据位于 `e5/evidence/hu-bo-20261029/ci/{normal-pr1,rejection-pr2,recovery-pr2}/`。拒绝时 PR #2 为 `OPEN / BLOCKED`，[普通合并日志](../e5/evidence/hu-bo-20261029/ci/rejection-pr2/merge-rejection.log) 记录策略阻止合并及退出码 1。修正预期后，PR #2 于 **2026-10-29 15:01:32 UTC** 合并，merge commit 为 **`701be1bee2e0246107a6638f5aed49e4bd349019`**，已与本次 GitHub API 查询核对。

main 当前仍要求 GitHub Actions App ID **15368** 的 **`e7-b-quality-gate`**；`strict=true`、`enforce_admins=true`、`required_approving_review_count=0`，通过 PR 合并，禁止强推。当前 main 对应检查成功，保护和 check-runs 快照见 `e7/evidence/verification-20261110/`。

## 归档、复现与范围

[归档清单](evidence-manifest.json) 固定原始日志、API 快照和运行源码的摘要；执行 `python3 e7/scripts/verify_archive.py` 可离线检查六项结果、CSV、镜像 ID、输入哈希、超时清理记录和 PR/提交对应关系。它只核验既有证据，不把历史运行描述成本次重新执行 Docker。

新工作流仍对 push/PR 执行语法检查、源文件与 Git 历史扫描、服务构建、镜像扫描、单测和完整门禁；`if: always()` 归档 `work/ci/`，保留 14 天。现有 CI 运行及下载附件属于审阅材料；待 CI 交叉验收、组长接收及合并后，再按最终 SHA 生成正式提交包。

本次验收不依赖 A11 服务，也不需要三名成员各重复同一套 CI；不把未收到的成员复核记为已完成。历史正常/拒绝/恢复演示已经完成，此次整理 PR 不冒充当时的演示 PR。
