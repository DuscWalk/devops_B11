# E4 要求与现状核对

2026-10-16；页号为实际页序。两版差异已逐页核对，采用能同时满足两版的证据准备方式。补充说明覆盖云平台为华为云。

| 要求 | 对应文件/证据 | 状态 |
| --- | --- | --- |
| 服务骨架、Compose、Dockerfile、一键构建（2、4、16 页） | 根 Makefile、services/draft、compose.yaml；胡博 full-run/build.log | 通过 |
| 基础镜像固定 digest、Python 哈希锁、系统版本记录（6–9 页） | Dockerfile、requirements-dev.lock、toolchain.lock | 通过；系统包导出实际版本，未宣称跨时间逐字节相同 |
| 非 root、docker.sock 权限和资源限制（9–13 页） | Dockerfile/Compose，verification/container-access.txt | app uid 10001 实测可以访问 Server |
| 配置不入仓库与镜像、密钥扫描（14–15、18 页） | .gitignore/.dockerignore/.env.example，secret-scan.txt；负向与清理后扫描 | 通过；.env 权限 600，未被跟踪 |
| 单测与预期失败冒烟（16–17 页） | test.log、smoke.json、smoke-build.log | 4/4，完整日志，预期缺少 make |
| 证据关联源码提交（19 页） | source-sha.txt、source-status.txt、SHA256SUMS.json | 已归档胡博本人的真实运行 |
| 每人独立运行，至少两位成员对照（19 页及手册） | MEMBER_RUN_TEMPLATE、CONTRIBUTIONS | 胡博完成；孙静怡/王硕及成员对照待完成 |
| 相邻组 README 复现（20 页） | HANDOFF | 待对方实际参与 |
| 学号作者与个人贡献（新增版 5、20 页） | E4 新提交作者 241276007；CONTRIBUTIONS | 胡博完成，其他成员贡献待补，不改旧历史 |
| 组长汇总统一提交（Other-Instructions.txt） | SUBMISSION.md、交接包 | 已准备胡博部分，待全组证据齐备 |

资源差异单列：原包 3.5 GiB 阈值与胡博转述的助教 2 GB 参考配置不一致。B11 显式适配且保留原模式；原模式拒绝、适配模式完整通过的两类结果都归档。不能把本次小型骨架跑通推断为后续所有论文负载都适用 2 GB。
