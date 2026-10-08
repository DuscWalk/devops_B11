# E3 实际执行证据

本目录只收选定的文本日志、元数据和小型补丁。运行入口默认写入被忽略的 `e3/work/`，通过 `--export-evidence` 导出新归档；已有证据不覆盖。

- `source.json`：当次 B11 主仓完整 SHA、工作区状态、实际输入文件摘要。若工作区非空，不能仅靠 HEAD 声称运行了干净提交。
- `environment.json`：实际环境与 B11 提案指纹；宿主与容器不同配置。
- `commands.json` / `logs/`：实际命令、工作目录、退出码、超时与输出。
- `observations.json` / `summary.json`：实际断言与总体结果，失败也保存。
- `checksums.json`：归档小文件摘要，不包括自身与工作副本。
- `mdfixer-prototype/`：现有自动本地原型的真实响应和产物，与四种人工参考补丁分开。
- `rejected/`：故意失败候选、原始失败日志和恢复依据。

教师课件中的已验证数字不作为本仓执行记录；A11 接收/重检未执行时保持明确标记。后续成员用自己的新目录追加，不改胡博原始记录。

## 2026-10-08 胡博实际归档

| 目录 | 结论与用途 |
| --- | --- |
| [hubo-clean-checkout-20261008](hubo-clean-checkout-20261008/summary.json) | 推荐阅读：干净克隆的最终本地复跑，67/67；源码 fe6a421，证据回归 5/5 |
| [hubo-local-20261008](hubo-local-20261008/summary.json) | 初始已提交版本 c854eaa 的本地 67/67，通过；当时证据回归 4/4 |
| [hubo-docker-20261008](hubo-docker-20261008/summary.json) | 实际 Docker 缺工具链与参考成功，3/3；包清单和镜像标识在目录内 |
| [hubo-docker-buildx-failure-20261008](hubo-docker-buildx-failure-20261008/summary.json) | 原始环境/CLI 故障，尚未进入构建；已通过脚本 fallback 解决 |
| [hubo-docker-classifier-failure-20261008](hubo-docker-classifier-failure-20261008/summary.json) | 真正缺 make 的 127 被旧分类器误拒；已修复并回归 |

[archive-audit-20261008.json](archive-audit-20261008.json) 记录 271 个归档文件的 SHA-256 核验、环境指纹复算和成功运行的源码输入/记录 commit 一致性。早期失败保留当时的 dirty 输入清单；不修改原结果。
