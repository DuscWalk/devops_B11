# E3 当前状态

更新：2026-10-08。**胡博的公共基线、验收、证据整合和交接工作已完成，可交给组员继续模块工作。** 组员 E3 复跑/审核及 A11 后续确认尚未发生，不将本人自动验证登记为他人确认。

## 已完成与实际验证

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

本地实际环境为 Ubuntu 22.04 / WSL Linux x86_64、GCC 11.4、GNU Make 4.3、Python 3.10.12；微型 Docker 参考环境为 Debian/GCC 14.2、GNU Make 4.4.1。它们都不是 E2 fzy 的 GCC13 环境。配置和环境指纹在对应 `environment.json`。

Docker 镜像 `b11/e3-tiny-reference:746ffdcc9379`，ID `sha256:bc646cd9fd597910d80544dbff05188bcc7ac2e5cab44178d305c28f328e5448`，仅存在于当前 Docker daemon，未发布/导出、未被 A11 接收。

## 已解决的真实失败

1. 首次 Docker 运行缺 buildx，legacy builder 不支持 `--progress`，构建尚未开始。保存 [原失败](evidence/hubo-docker-buildx-failure-20261008/summary.json)；脚本增加进程级 legacy fallback，不安装插件或修改全局 Docker 配置。
2. legacy builder 真正返回缺 make 的 127；原验收代码错误排除了 127，导致误判。保存 [误判记录](evidence/hubo-docker-classifier-failure-20261008/summary.json)；已修正分类并新增回归，最终再次执行通过。

## Git 与来源

工具和文档初始提交 `c854eaa`；Docker 分类修复 `fe6a421`。干净克隆使用完整 `fe6a4215a4c63a7652161ca93c9630a57af03015`；随后仅追加证据和完成状态。当前交接分支 `feat/e3-hubo-baseline`，最终提交 SHA 从 Git 获取。

Docker 运行的 source.json 记录了未提交的旧本地证据目录；源代码输入摘要仍全部匹配 fe6a421，审计明确保留其原始工作区状态，不把它改写为干净。

## 未完成与下一步

- 孙静怡：本人复跑 DRAFT 和 fzy，补模块证据；当前 Tiny Greeting 参考成功不代表 fzy 的 E3 新运行。
- 王硕：审核固定报告和四风格参考，复跑原型并明确支持范围；参考 Patch 不是自动原型能力。
- 全体：组员交叉复核和人工答案审阅待真实执行，按 [HANDOFF](HANDOFF.md) 回传分支与结果。
- 胡博/A11：环境哈希提案确认、真实镜像/产物接收、真实检测报告与重检在后续推进；当前 `PROPOSED_B11_ONLY` / `NOT_RUN` 保持明确。
- 基础镜像 tag 和 APT 包未完全固定，宿主哈希未含完整库清单；记录实际 image ID/digest 和限制，不声称完全可复现部署环境。

不阻塞 B11 本次独立基线交接，E3 完整小组提交仍需收到组员材料后由胡博整合。
