# GitHub CI 与合并门禁证据

仓库：[DuscWalk/devops_B11](https://github.com/DuscWalk/devops_B11)。默认分支 `main` 要求 `e7-b-quality-gate` 检查（GitHub Actions App ID `15368`）、strict 更新、enforce admins、零审批和对话解决。

- `normal-pr1/`：PR #1 正常检查运行 [40895134404](https://github.com/DuscWalk/devops_B11/actions/runs/40895134404) 的 artifact、PR 合并 JSON；合并提交 `2d3d857abf5133619ef302e89d2f9d6b0f85ab57`。
- `rejection-pr2/`：PR #2 故意错误断言的失败运行 [40895904554](https://github.com/DuscWalk/devops_B11/actions/runs/40895904554) 的 artifact、失败日志、`OPEN / BLOCKED` 状态、保护规则快照和合并拒绝输出。错误测试结果为 1 failed、25 passed；合并尝试退出码为 1。
- `recovery-pr2/`：修复后的运行 [40896410596](https://github.com/DuscWalk/devops_B11/actions/runs/40896410596) artifact、PR 检查列表、保护规则与最终合并 JSON。26 项单测和五个场景通过；PR #2 合并提交 `701be1bee2e0246107a6638f5aed49e4bd349019`。
- `40870191130/`：初次 push CI artifact，同样五场景全部通过。

GitHub Actions artifact 保留 14 天；下载副本随本仓库归档。
