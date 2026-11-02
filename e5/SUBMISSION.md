# B11 第五次实验提交说明

本次提交为 E5：DRAFT 单次论文流程复现。整理日期为 2026-11-02（America/New_York）。

## 提交定位

- 小组 / 轨道：B11 / B-DRAFT。
- 仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11
- 分支：`main`；固定标签：`e5-b11-submission-20261102`。
- 完整 SHA：执行 `git rev-parse e5-b11-submission-20261102^{commit}`，或查看附件 `MANIFEST.json`。
- 小组报告：[REPORT.md](REPORT.md)；要求对照：[REQUIREMENTS_CHECK.md](REQUIREMENTS_CHECK.md)；贡献：[CONTRIBUTIONS.md](CONTRIBUTIONS.md)。
- 原始运行和候选：[成员证据](evidence/sun-jingyi-20261102/README.md)；整合核验：[audit.json](evidence/submission-20261102/audit.json)。
- 本次原运行 work 路径：`/home/duscwalk/241250112/e5-20261102/work/`；所需输入、日志、候选、镜像和退出码均已导出到上述证据目录。

## 可粘贴到课程平台

B11 完成 E5 的 B-DRAFT 单次流程复现。采用课程 Tiny Greeting 样例和固定基础镜像 digest，真实记录 RUN make 缺少 make 的失败；依据本次日志生成错误驱动和上下文驱动两类提示，保存各自 Codex 原始回复、Dockerfile、来源和选择理由。原选中候选下载停滞后保留中止日志，另存华为 HTTPS 镜像源调整版本，最终 Docker build 退出 0。按本次构建得到的同一完整 image ID 禁网运行，退出 0，stdout 精确为 hello E3 加换行，容器清理记录完整。

主运行来自孙静怡独立目录，胡博接收分支并核验、汇总。报告说明课程参考代码与本组实际操作、模型版本记录限制、论文方法对应及微型样例的适用范围。学院分配的 2 GB 主机完成本次实验；课程通用 4 GiB 资源自检失败原样保留。本次只提交 E5，E6 自动服务与 E7 CI/门禁属于后续阶段。

## 附件与复现

附件为 `B11-E5-20261102.zip`，内含 `repository/e5/`、`repository/docs/e5/`、提交定位与逐文件 SHA-256 清单。它是 E5 专项材料包，源码快照足够执行 [README](README.md#复现-e5) 的 E5 复现步骤；完整 Git 历史由仓库固定标签取得。未将 E2–E4 或 E6/E7 的运行结果列为本次成绩依据。

解压后先读 `START_HERE.md`，再读小组报告及证据索引。需要完整仓库时，克隆 GitLab 并检出上述标签。材料已准备，不代表已上传 LMS；平台附件格式和截止时间以实际通知为准。
