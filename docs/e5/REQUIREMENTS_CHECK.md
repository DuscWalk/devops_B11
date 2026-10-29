# E5–E7 验收状态（B11 / DRAFT）

截至 2026-10-29。课程原验收清单见 [05_验收清单](05_验收清单_课程原文.md)。

|要求|状态|证据或待办|
|---|---|---|
|学号、小组、轨道、云环境|PASS|胡博 241276007，B11 / B-DRAFT；[实验报告](REPORT.md)|
|课程包来源与 SHA-256|PASS|E5-7 ZIP 内 77 项 SHA-256 全部匹配；[来源清单](Student_Cloud_MANIFEST.sha256.json)|
|E5 失败日志、两类提示、候选来源|PASS|[E5 证据](../../e5/evidence/hu-bo-20261029/e5-02/)，来源和回复见候选 provenance|
|E5 候选构建、同一镜像运行、输出 hello E3|PASS|[构建退出码](../../e5/evidence/hu-bo-20261029/work/e5-02/candidate-build-exit-code.txt)、[镜像 ID](../../e5/evidence/hu-bo-20261029/work/e5-02/candidate-image-id.txt)、[运行输出](../../e5/evidence/hu-bo-20261029/work/e5-02/candidate-run.log)|
|E6 自动候选构建、JSON 报告、输入副本与哈希|PASS|[E6 结果](../../e5/evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/result.json)；课程校验器返回 `passed: true`|
|E7 服务单测和五场景|PASS|[gate-result.json](../../e5/evidence/hu-bo-20261029/e7-hubo-20261029-customtest/gate/gate-result.json)、[results.csv](../../e5/evidence/hu-bo-20261029/e7-hubo-20261029-customtest/gate/results.csv)；25 项单测及五个场景通过|
|B11 自主增加的测试|PASS|[多阶段候选拒绝测试](../../e5/labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py)，已包含在 25/25 单测中|
|密钥扫描（工作区、历史和服务镜像）|PASS|[工作区与历史](../../e5/evidence/hu-bo-20261029/secret-scan.txt) 扫描 1576 个文件；[服务镜像](../../e5/evidence/hu-bo-20261029/build-hubo-20261029-customtest/image-secret-scan.txt) 未发现问题|
|GitHub 正常 CI、失败 PR、修复恢复|PENDING|`gh auth status` 显示未登录；尚未创建课程要求的组级 GitHub 仓库或运行 CI|
|main 分支保护、合并拒绝和最终合并记录|PENDING|需要 GitHub 仓库权限；无运行链接、artifact 或合并记录|
|实验报告与证据备份|PASS|报告和运行证据已归档在本仓库 E5 功能分支|

课程 doctor 的 4 GiB 通用资源检查在学院分配的 2 GB 主机上会失败；按实际实验步骤继续后，E5、E6、E7 均完成。本结论只覆盖微型样例与课程测试。
