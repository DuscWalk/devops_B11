# E5 作业要求核对

范围依据：[E5 课件逐页文字](../docs/e5/E5_逐页文字.md) 第 17、19、20 页。通用学生包中的 E6/E7 验收不作为本次 E5 的前置项。

| E5 要求 | 核验结果 | 材料 |
| --- | --- | --- |
| 小组、轨道、环境、仓库与版本 | 齐全 | [报告](REPORT.md)、[提交说明](SUBMISSION.md) |
| 输入与所用代码 | 已保存输入副本及课程脚本；源码摘要与原 ZIP 一致 | [源码清单](evidence/sun-jingyi-20261102/source/manifest.json)、[输入](evidence/sun-jingyi-20261102/e5-01/project/) |
| 缺 make 的真实失败日志与退出码 | PASS：Docker build=1，RUN 层=127，驱动完成采集=0 | [原始构建](evidence/sun-jingyi-20261102/e5-01/iter-01/build/) |
| 错误驱动及上下文驱动提示 | PASS：从归档输入和日志重新生成，与两份原提示逐字一致 | [接收核验](evidence/submission-20261102/audit.json) |
| 候选正文、原始回复与来源 | PASS：两类候选及代码块一致；平台、时间、版本不可见限制如实记录 | [候选目录](evidence/sun-jingyi-20261102/candidates/) |
| 候选选择与修改说明 | 已记录初选、网络中止、换源差异和最终选择 | [selection.json](evidence/sun-jingyi-20261102/selection.json) |
| 手工复建成功 | PASS：最终候选 build=0；日志真实编译 `main.c` | [构建记录](evidence/sun-jingyi-20261102/candidate-build-02/) |
| 使用同一镜像 ID 验证输出 | PASS：禁网运行 exit=0，精确输出 `hello E3\n` | [运行验证](evidence/sun-jingyi-20261102/verification/) |
| 对照论文步骤，解释实际做法与限制 | 齐全：微型样例、两类提示、同会话候选、单次复现 | [小组报告](REPORT.md) |
| 证据路径、摘要与复现说明 | PASS：归档摘要核验；新输出目录的复现步骤已提供 | [README](README.md)、[接收核验](evidence/submission-20261102/audit.json) |
| 组内分工：王硕独立复跑及交叉核对 | 已接收：回放组内候选的复跑记录、与孙静怡结果的对照、63 项摘要全部匹配；运行命令的镜像 ID 记录按组长确认保留现状 | [王硕报告](WANG_SHUO_REPORT.md)、[接收核验](evidence/submission-20261102/wang-shuo-audit.json) |
| 课程资源自检 | 原始 FAIL：1.7 GiB 低于通用 4 GiB；学院 2 GB 主机已实际完成样例 | [doctor](evidence/sun-jingyi-20261102/preflight/doctor.log) |

E5 技术流程和提交材料已完成。以上 PASS 指已核验的真实记录，不表示教师已评分、LMS 已上传或自动核验等同于成员人工签字。E5 课件没有把新增 GitHub 仓库、CI 门禁或 A11 的业务结果列为本次提交前提。
