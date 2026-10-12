# E3 作业要求核对与 main 集成记录

日期：2026-10-12。胡博明确要求“对照作业要求检查，确认后合并到 main 上并推送”。依据归档的 E3 原 PPTX（与 lab3 原文件 SHA-256 一致），按 B11 的 B 组职责核对。

结论：B 组要求的技术材料及运行证据齐全，已将修复分支快进合入 main，保留成员历史。组员本人交叉复核仍需补录，未登记为已完成；本次合并不代表 LMS 已提交。

页号采用 PPTX 文件页序。

| 课件要求 | 页序 | 核对结果与材料 |
| --- | --- | --- |
| 固定 DRAFT 项目、构建及功能验证命令 | 6–8、29、32 | fzy 固定 SHA 28195b3a709995354b6c33cec9bb7c9f81532eb6；[项目](../draft/PROJECT.md)、[E3 README](../draft/e3-fzy/README.md) 写明构建、31 测试/99 断言及 alpha 输出判据 |
| 构建失败可定位，参考修复可构建并运行 | 6、30–32 | [Tiny Docker](evidence/draft-sjy-20261010-docker-https/summary.json) 3/3；[fzy](evidence/draft-sjy-20261010-fzy-pinned/summary.json) 5/5；日志确有 make: not found，参考输出及断网验证通过 |
| 固定 MD 报告与同版本 Makefile | 6、33 | [报告](../mdfixer/examples/md_report.json) 与 [固定源码及 bundle](../fixtures/mdfixer-project/source.json) 的 commit 一致，文件与 bundle 摘要正确 |
| 人工参考补丁、理由及四种声明风格 | 33–36 | [四风格 fixtures](fixtures/README.md) 分离 before/reference/oracle；来源为 B11_REFERENCE_ORACLE/MANUAL，未冒用教师文件或 A11 报告 |
| Patch 可应用，头文件变化后不 clean 仍重建 | 35–36 | [公共运行](evidence/hubo-mdfixer-fix-20261012/observations.json) 记录旧值 1 / clean 2 / 修复后增量 3；implicit 的 main.d 含 config.h |
| 无效候选拒绝及原文件恢复 | 37 | [拒绝证据](evidence/hubo-mdfixer-fix-20261012/rejected/) 含四风格真实失败、拒绝和摘要；恢复后构建/运行通过 |
| README、环境、命令、日志、仓库/SHA、个人贡献 | 9–10、12 | [状态](STATUS.md)、[贡献](CONTRIBUTIONS.md)、[交接](HANDOFF.md) 及证据 source/environment/commands/logs 齐全 |
| 失败与未完成事项如实记录 | 9 | [修复前失败](evidence/mdfixer-review-failure-20261012/README.md) 保留；支持限制、RV-01、A11 后续事项分别登记 |
| 相互检查、他人可复跑 | 10 | 独立干净检出已复现；孙静怡/王硕本人的人工复核记录尚未收到，继续按 RV-01 补录 |

## 证据有效性

本次核验 17 份归档摘要清单，共 740 个文件；核对所选三次成功运行的源码提交、命令记录和原始日志。详见 [机器审计记录](evidence/e3-requirements-audit-20261012.json)。

当前 139 个被测输入与 298a8db246dfdf1a40a3477ba4c2faa64694e95a 的干净检出运行一致：公共基线 67/67、MDFixer 回归 17/17、E2 公共回归 20/20、证据回归 6/6。统计有包含关系，不相加。本次未重复运行未变化的实现。

Docker/fzy 沿用 10 月 10 日真实运行结果，本次未重建镜像。相关脚本、Dockerfile、源码 fixture 和功能判据未变化；draft/README.md 与 draft/E3_PLAN.md 仅追加了进度说明，已单独审阅。

## Git 与剩余事项

- 合入前 origin/main：05d9e5e06c89a9f0b7bda7eb12f9fcbea79da1b0。
- 已审阅并合入的修复分支：565e827032461b221816145b23cd1f682a759cf6；实现提交 298a8db，证据提交 565e827。
- main 快进保留既有历史；随后仅追加本核对记录和集成状态文档，不修改已验证实现。实际最终 SHA 以 git rev-parse HEAD 为准。
- RV-01 人工复核继续登记真实执行人和结论；自动验证不替代本人审核。
- LMS 提交格式、截止日期和教师权限未从平台核实，本次未向 LMS 提交，也未创建正式 E3 tag。
- 课件第 4、10 页将对组真实数据联调安排在 E12；A11 接收、检测器重检及环境哈希确认不作为本次合并前置条件。NOT_RUN / PROPOSED_B11_ONLY 保持明确。
