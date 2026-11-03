# B11 E6 提交说明

- 仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11
- 本次审阅分支：`feat/e6-submission`
- 内容入口：[实验报告](REPORT.md)、[要求核对](REQUIREMENTS_CHECK.md)、[复现步骤](README.md)
- 附件：`B11-E6-20261103-review.zip`，内含 `START_HERE.md`、`MANIFEST.json`、`repository/e6/`、`repository/docs/e6/` 及需要的原始学生 ZIP。
- 完整提交 SHA 和每个附件文件的 SHA-256 固定写入 `MANIFEST.json`；ZIP 整体摘要在同名 `.sha256` 文件中。

本次分支以已提交的 E5 `2e9d3527494adbffbaf11503ae56137cd42c8bc5` 为基础，供组内审阅。分支名可以继续前进，提交时应填写附件中固定的 SHA。若后续合并 main 并以合并提交交作业，应重新生成与该 SHA 对应的附件。

2026-11-03 补充：远端已有王硕的 `feat/e6-auto-build`（`d95fefa`），尚待整合；组内后续按 [交接安排](HANDOFF.md) 执行。上述 ZIP 仍是固定在 `4abf849` 的审阅包，不含王硕新分支和本次交接文档。最终交付时生成新的包和完整 SHA。

LMS 说明可使用：

> B11 / B-DRAFT，E6 论文 1 MVP。CLI 自动完成初始缺 make 失败、候选修复构建以及同一完整镜像 ID 的禁网运行；输出 hello E3，退出 0。新增多阶段候选拒绝测试，重新构建后 25 项单元测试及课程五场景门禁通过。输入副本、JSON、原始日志、候选回复与来源、源码字段对照和复现步骤见附件。代码以附件 MANIFEST.json 中的完整提交 SHA 为准。

提交前组内可按报告解释自动流程和新增测试。课程未要求等待 A11 或每名成员单独复跑；现有成员贡献按实际材料注明。LMS 的具体上传格式与截止时间以当次通知为准。
