# B11 第四次实验提交说明

提交材料整理日期：2026-10-21（America/New_York）。本版本集中三位成员的工程成果、运行证据和组长汇总报告，可作为本组仓库提交入口；相邻组 README 复现尚未提供记录，报告中保持待补。

## 提交定位

- 小组：B11；配对组 A11。
- 成员：胡博 241276007、孙静怡 241250112、王硕 241250110。
- 仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11
- 分支：main；固定标签：`e4-b11-submission-20261021`。最终完整 SHA 由 `git rev-parse e4-b11-submission-20261021^{commit}` 查询，也记录在提交 ZIP 的 MANIFEST.json。
- 实验报告：[REPORT.md](REPORT.md)。成员贡献：[CONTRIBUTIONS.md](CONTRIBUTIONS.md)。要求核对：[REQUIREMENTS_CHECK.md](REQUIREMENTS_CHECK.md)。
- 原始日志：[胡博](evidence/hu-bo-20261016/README.md)、[孙静怡](evidence/sun-jingyi-20261019/README.md)、[王硕](evidence/241250110-20261021/README.md)。
- 复现对照：[COMPARISON.md](COMPARISON.md) 和 [机器报告](evidence/submission-20261021/member-comparison.json)。
- 原课件、教师实验包和两版差异：docs/e4/。原始资料与成员证据均保留，不修改其日期、SHA 或作者。

## 可粘贴到课程平台

B11 完成 E4 可重复工程环境，将教师 B-draft 服务骨架接入原 E2/E3 仓库。采用固定基础镜像 digest、Python 依赖哈希锁、实际工具版本清单、非 root 服务及 Compose、一键 doctor/build/test/smoke/scan。按助教参考 2 GB 配置，在华为云实际可见内存 1.7 GiB、无 swap 的服务器上完成三位成员的独立目录运行：每人服务单测 4/4，冒烟准确记录缺少 make 的预期失败和完整日志，正常密钥扫描通过，假 Key 可检出、清理后通过。三人的工具清单完全一致；胡博与孙静怡使用同一源码 SHA，王硕使用仅增加归档材料的后继版本，运行文件一致，差异已单列说明。

组长已汇总三人贡献和原始日志、整合分支并准备提交版。相邻组仅按 README 复现尚无提供记录；未将自动运行记作其他成员人工签字或组间互评通过。未代上传 LMS。

## 复现和附件

正式复现从真实 Git 远端克隆后 checkout 提交标签，再依 [README](README.md) 设置本地学号身份运行 `make all`。ZIP 中 repository/ 是完整已跟踪源码快照，不含 .git，不能替代正式 Git 历史扫描所需的克隆。只阅读报告和日志可直接解压附件。

镜像保留在课程服务器 Docker daemon，名称 e4-draft:<学号>；没有发布外部 registry 地址。本地 image ID 不冒充可拉取的 registry RepoDigest。附件不含 .env、SSH 私钥、临时假 Key 或缓存。平台未在现有通知中规定固定文档格式或截止时间，按 LMS 实际入口提交。
