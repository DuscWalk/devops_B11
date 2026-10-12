# E3 当前状态

更新：2026-10-12。**胡博已修复 MDFixer、核对课件并合入 main，公共基线与模块自动验收通过；组员人工交叉复核和正式提交仍待完成。** 按运行日期区分来源，自动执行不代表成员人工审核。

## 三人进度与下一步

| 成员 | 已完成 | 接下来负责 |
| --- | --- | --- |
| 孙静怡 / DRAFT | 固定 fzy 故障与参考成功、公共/Docker 复跑、脚本修正和证据归档 | 本人审阅预期与日志；复核 main 中的 MDFixer 并记录结论 |
| 王硕 / MDFixer | 已交回四风格扩展；胡博修复源码/接口并补齐 17 项模块回归 | 审阅修复和支持范围，复核 DRAFT；孙静怡复核 MDFixer |
| 胡博 / 公共与集成 | 公共基线、环境提案、证据入口；10 月 12 日修复 MDFixer、恢复文档、核对作业要求并合入 main | 收齐 RV-01，再确定正式提交与 tag |

## 10 月 12 日 MDFixer 修复与复验

本轮由胡博明确授权 Codex 执行；模块原作者及王硕的 E3 扩展保留，详见 [模块记录](mdfixer-notes.md)。修复来源为 fix/e3-mdfixer-baseline，已快进合入 main，保留 main 和 MDFixer 全部历史。[作业要求核对](REQUIREMENTS_CHECK.md) 记录课件条目、证据与剩余事项。

| 项目 | 本轮结果 | 证据 |
| --- | --- | --- |
| 修复前最新分支 | 3af8c22 有 3 个 Python 文件语法错误；统一基线失败，四风格测试未能导入 | [失败复查](evidence/mdfixer-review-failure-20261012/README.md) |
| E2 正式入口 | 通过；含 20 个公共回归、17 个 MDFixer 回归、契约与真实演示 | [运行日志](evidence/hubo-mdfixer-fix-20261012/logs/002-e2-validation.txt) |
| MDFixer 自动补丁 | 四风格及累计修复实际执行 REPAIR、产物摘要、git apply、oracle 字节对照、构建与头文件重编译 | [模块日志](evidence/hubo-mdfixer-fix-20261012/logs/002-e2-validation.txt) |
| 公共本地基线 | 67/67，82 条外部命令；证据工具回归 6/6 | [summary](evidence/hubo-mdfixer-fix-20261012/summary.json) |
| 本次源码 | 独立干净检出的完整 SHA、实际输入摘要和环境 | [source](evidence/hubo-mdfixer-fix-20261012/source.json)、[environment](evidence/hubo-mdfixer-fix-20261012/environment.json) |
| Docker / fzy | 本轮未修改相关执行代码，未重新运行；下方保留 10 月 10 日真实记录 | [DRAFT 记录](draft-notes.md) |

各层测试数量有包含关系，不相加。人工参考测试和自动补丁测试分别验证；真实 A11 检测器重检仍为 NOT_RUN，环境提案仍为 PROPOSED_B11_ONLY。修复后的技术验收不代表组员已经完成人工复核。

## 10 月 10 日 DRAFT 新增结果

本轮由孙静怡授权 Codex 执行，详见 [模块交接](draft-notes.md)。

| 项目 | 已归档结果 | 证据 |
| --- | --- | --- |
| 公共本地入口 | 67/67 检查，82 条命令 | [local-final](evidence/draft-sjy-20261010-local-final/summary.json) |
| Tiny Greeting Docker | 3/3：缺 make、参考成功及断网验证 | [docker-https](evidence/draft-sjy-20261010-docker-https/summary.json) |
| 固定 fzy | 5/5；断网 clean 构建、31 测试/99 断言、help 与精确筛选输出 | [fzy-pinned](evidence/draft-sjy-20261010-fzy-pinned/summary.json) |
| 证据基础设施回归 | Windows/WSL 各 6/6；新增 draft 输入追溯并修正 Windows 超时 | [模块说明](draft-notes.md) |
| 归档核验 | 9 次运行共 337 文件摘要一致，输入匹配各自源提交，保留失败记录 | [审计](evidence/draft-sjy-audit-20261010.json) |

各层检查数不相加。新镜像 ID、基础 digest、实际环境及失败处理见模块记录；镜像未发布或交付 A11。新结果不覆盖下方历史记录。

## 胡博 10 月 8 日已完成与实际验证（历史记录）

| 项目 | 实际结果 | 证据 |
| --- | --- | --- |
| E2/E3 课件归档 | 原 PPTX 摘要一致；27/39 页逐页文字与要求整理；本地链接已核验 | [docs](../docs/README.md)、[归档审计](evidence/archive-audit-20261008.json) |
| E2 正式入口 | 整体退出 0，包含原公共契约/反例、20+6 回归、模块样例和本地修复 | [当前运行日志](evidence/hubo-clean-checkout-20261008/logs/002-e2-validation.txt) |
| E3 本地统一入口 | 67/67 项行为与完整性检查通过；82 条外部命令有记录 | [summary](evidence/hubo-clean-checkout-20261008/summary.json)、[观察](evidence/hubo-clean-checkout-20261008/observations.json) |
| 四种参考 Patch | 修复前旧值 1 / clean 2；修复后再次改头文件，不 clean 输出 3；Implicit 的 .d 含 config.h | [人工样例](fixtures/README.md)、[原始日志](evidence/hubo-clean-checkout-20261008/commands.json) |
| 无效候选拒绝和恢复 | 四风格均实际构建失败且拒绝，恢复原 Makefile 后重新构建/运行通过 | [rejected](evidence/hubo-clean-checkout-20261008/rejected/) |
| 现有 MDFixer 原型 | 1 个候选接受，3 产物可读，patch/build/test/header-change 通过，RD 保留 | [原型结果](evidence/hubo-clean-checkout-20261008/mdfixer-prototype/result.json) |
| 异根读取与损坏拒绝 | 新产物复制到消费方目录后可读，篡改摘要被拒绝；不是 A11 接收 | [读取回执](evidence/hubo-clean-checkout-20261008/artifact-receipt.json) |
| Docker 实际运行 | 3/3 断言通过，12 条命令；缺 make 退出 127；参考镜像与断网重建输出 hello E3 | [Docker summary](evidence/hubo-docker-20261008/summary.json)、[失败结果](evidence/hubo-docker-20261008/broken-result.json) |
| 证据基础设施回归 | 5/5：哈希配置变化、日志保留、超时、禁止覆盖、Docker 故障分类 | [回归日志](evidence/hubo-clean-checkout-20261008/logs/001-e3-evidence-regressions.txt) |
| 干净克隆复现 | 不含原工作区或 .venv 的独立 clone，以已安装 Python 环境重跑本地入口，通过 | [源码快照](evidence/hubo-clean-checkout-20261008/source.json) |
| 证据归档核验 | 271 个小文件摘要及两个环境指纹复算一致；各成功运行输入摘要匹配记录的 Git commit | [审计](evidence/archive-audit-20261008.json) |

数量分层统计，不把相互重叠的回归、行为断言和重复复跑相加为“独立测试数”。

胡博 10 月 8 日记录的本地环境为 Ubuntu 22.04 / WSL Linux x86_64、GCC 11.4、GNU Make 4.3、Python 3.10.12；微型 Docker 参考环境为 Debian/GCC 14.2、GNU Make 4.4.1。它们都不是 E2 fzy 的 GCC13 环境。配置和环境指纹在对应 `environment.json`。

历史 Docker 镜像 `b11/e3-tiny-reference:746ffdcc9379`，ID `sha256:bc646cd9fd597910d80544dbff05188bcc7ac2e5cab44178d305c28f328e5448`，记录于该次运行的 daemon，本次未核实其当前可用性；未发布/导出、未被 A11 接收。

## 已解决的真实失败

1. 首次 Docker 运行缺 buildx，legacy builder 不支持 `--progress`，构建尚未开始。保存 [原失败](evidence/hubo-docker-buildx-failure-20261008/summary.json)；脚本增加进程级 legacy fallback，不安装插件或修改全局 Docker 配置。
2. legacy builder 真正返回缺 make 的 127；原验收代码错误排除了 127，导致误判。保存 [误判记录](evidence/hubo-docker-classifier-failure-20261008/summary.json)；已修正分类并新增回归，最终再次执行通过。

## Git 与来源

工具和文档初始提交 `c854eaa`；Docker 分类修复 `fe6a421`。干净克隆使用完整 `fe6a4215a4c63a7652161ca93c9630a57af03015`；随后追加证据和完成状态。原交接分支 `feat/e3-hubo-baseline` 的归档提交为 `d994302`，已由 `1e61e6b` 合入 `feat/draft`。DRAFT 新材料归档提交为 `98dae53`；这些是历史归档来源；DRAFT 已进入 main，本轮修复及证据已合入 main，尚未建立正式 E3 提交 tag。

Docker 运行的 source.json 记录了未提交的旧本地证据目录；源代码输入摘要仍全部匹配 fe6a421，审计明确保留其原始工作区状态，不把它改写为干净。

## 未完成与下一步

- 孙静怡：DR-01/DR-02 运行材料已齐；本人审阅人工预期与日志，交回分支/SHA，并在王硕材料到齐后复核 MDFixer。
- 王硕：审阅本轮修复、四风格实际输出及支持/拒绝范围；按 HANDOFF 复核 DRAFT。
- 全体：组员交叉复核和人工答案审阅待真实执行，按 [HANDOFF](HANDOFF.md) 回传分支与结果。
- 胡博：代码、证据与文档已合入 main，课件要求及摘要已核对；收齐 RV-01 后完成 LMS 提交整理与正式版本标记。
- 胡博/A11：环境哈希提案确认、真实镜像/产物接收、真实检测报告与重检在后续推进；当前 `PROPOSED_B11_ONLY` / `NOT_RUN` 保持明确。
- 基础镜像 tag 和 APT 包未完全固定，宿主哈希未含完整库清单；记录实际 image ID/digest 和限制，不声称完全可复现部署环境。

A11 不阻塞 B11 本次独立基线交接；当前剩余的是组员人工复核和提交整理。
