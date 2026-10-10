# E3 提交与归档清单

小组 B11，配对 A11。使用原仓 `https://git.nju.edu.cn/devops_b11/devops-project-b11`。本次当前材料入口 `e3/README.md`；提交格式、截止日期和教师权限按 LMS 作业通知，不代提交。

| 要求 | 材料 |
| --- | --- |
| 课程要求与原文件 | docs/README、两份 PPTX、逐页文字、sources.json |
| DRAFT 项目/验证条件 | draft/PROJECT、e3/fixtures/draft、本人新增运行证据 |
| 固定 MD/Makefile/参考 Patch | fixtures/mdfixer-project、e3/fixtures/mdfixer、运行证据 |
| 环境/命令/日志 | environment.json、commands.json、observations.json、logs/、summary.json |
| 人工预期与实际观察分开 | fixtures/*/oracle.json 对照 evidence |
| 仓库/SHA/贡献 | CONTRIBUTIONS、Git 历史、实际源码 source.json |
| 未完成/失败/下一步 | STATUS、Backlog、HANDOFF |

提交前由胡博合入成员已复核的分支，整合文档并运行公共入口；另记录 Docker 检查结果。不得把只有胡博准备的底座标为三位成员全部完成。若最终用 ZIP，按固定提交导出，附完整 SHA；不带 `.git`、`.venv`、e3/work 或镜像归档。

## 2026-10-10 提交准备状态

| 材料/动作 | 负责人 | 状态 |
| --- | --- | --- |
| 公共基线、人工样例、历史本地/Docker 证据 | 胡博 | 已完成，保留 10 月 8 日来源 |
| 固定 fzy 与 DRAFT 失败/成功运行材料 | 孙静怡 | 已完成，见 [模块记录](draft-notes.md)；待本人审阅与组内接收 |
| MDFixer 模块复跑、四风格审阅、支持范围说明 | 王硕 | 当前分支尚未收到新增 E3 模块交接材料 |
| 两模块人工交叉复核 RV-01 | 孙静怡、王硕；胡博归档 | 待执行 |
| 最终合并、公共与 Docker 验证、提交材料核对 HB-07 | 胡博 | 待模块与复核材料齐备后执行 |

历史 E2 tag `e2-b11-submission-20260922` 保留。当前 `feat/draft` 包含公共基线和 DRAFT 新材料；全组完成并审阅后再建立 E3 正式提交 tag，不提前把准备分支标成完整小组提交。分工细项见 [任务表](Backlog.md) 和 [交接操作](HANDOFF.md)。
