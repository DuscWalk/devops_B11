# E6 要求核对

依据 [E6 逐页文字](../docs/e6/E6_逐页文字.md)，B11 采用 B 轨道。

| 课件 | 要求 | 结果与证据 |
| --- | --- | --- |
| 2–4、15 页 | 云服务器 CLI 读取 E5 候选 | 已完成；[入口源码](labs/B-draft/scripts/lab_cloud.py)、[调用记录](evidence/hu-bo-20261029/e6-hubo-20261029-mirror/runner/command.json) |
| 11–13 页 | 固定 FROM、保留项目指令、两轮构建 | 已完成；[首轮](evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/iter-01/Dockerfile)、[候选](evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/iter-02/Dockerfile) |
| 13、18 页 | 第一轮 MISSING_MAKE，第二轮成功 | 已完成；[result.json](evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/result.json) 和同目录原始日志 |
| 14、18 页 | 同一完整镜像 ID 禁网运行，退出 0、hello E3 | 已完成；[image inspect](evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/iter-02/image-inspect.json)、[输出](evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/verify.log)；课程校验器通过 |
| 16–17 页 | 至少一项自己的测试，重建并运行 | 已完成：labs 副本的 [本组新增测试](labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py)、[重新构建后 25 项单测](evidence/hu-bo-20261029/build-hubo-20261029-customtest/unit-tests.log) 和 [门禁](evidence/hu-bo-20261029/e7-hubo-20261029-customtest/gate/gate-result.json)。王硕接入根目录的 `test_autobuild.py`、`test_workflow_failures.py` 来自课程参考实现，不计为本组原创新增测试；两套目录的测试数量不相加 |
| 17 页 | 定位与报告字段对应的源码 | 已整理；[报告](REPORT.md)中的函数、行号、字段和实际值对照 |
| 17 页 | 输入副本、JSON、原始日志 | 已归档；[证据索引](EVIDENCE.md)、[212 项摘要](evidence/hu-bo-20261029/SHA256SUMS.json) |
| 17 页 | 候选原始回复与来源 | 已归档；[候选来源](evidence/hu-bo-20261029/candidate/provenance.json)，历史路径迁移见证据索引 |
| 17 页 | 仓库地址、SHA、自己的代码修改、报告 | 分支 `feat/e6-submission`（合并提交 `8d63bee`）；SHA 在交付附件 `MANIFEST.json` 中固定；[提交说明](SUBMISSION.md)、[来源与贡献](SOURCES_AND_CONTRIBUTIONS.md) |

历史环境自检因通用 4 GiB 要求未通过，保留原始结果；学院 2 GB 主机上的上述构建和运行已有实测证据。提交范围为 E6，不使用 E7 的 CI 或保护设置作为 E6 完成条件。

2026-11-03 又使用本次提交的复现脚本重新运行全部步骤，通过；新结果和 447 项服务器原始文件摘要见 [复现元数据](reproduction.json) 及 [报告](REPORT.md)。最终执行的 33 项源码摘要与提交内容一致。
