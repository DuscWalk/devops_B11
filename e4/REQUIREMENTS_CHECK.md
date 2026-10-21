# E4 作业要求核对

更新：2026-10-21。引用页号为 PPT 实际页序；补充通知覆盖平台为华为云，并由组长汇总每人贡献统一提交。

| 作业要求 | 当前证据 | 结果 |
| --- | --- | --- |
| 服务骨架、Dockerfile、Compose、一键构建（2、4、16 页） | services/draft、compose.yaml、Makefile；三人 build.log | 通过 |
| digest、哈希依赖和系统版本记录（6–9 页） | 固定基础镜像、requirements-dev.lock、各自 toolchain.lock | 通过；系统包导出实际版本，未承诺跨时间位级相同 |
| 非 root 及 docker.sock 组权限（9–13 页） | Dockerfile/Compose；胡博 container-access.txt | app UID 10001 实测可访问宿主 Server |
| 密钥不入仓库/镜像，扫描器能报错（14–15、18 页） | 三人正常/假 Key/清理后扫描；.gitignore/.dockerignore | 通过，假 Key 未提交，日志值遮蔽 |
| 单元测试与预期失败冒烟（16–17 页） | 三份 test.log、smoke.json、smoke-build.log | 三人均 4/4；预期缺少 make，完整日志一致 |
| 证据对应源码提交（19 页） | 每人 source-sha.txt、source-status.txt；COMPARISON.md | 已逐个对应；王硕版本差异单列 |
| 每人运行，至少两人同 SHA 对照（19 页、手册） | 三人独立目录日志；胡博/孙静怡使用同一 SHA | 运行证据齐全，三人结果已机器核验 |
| 学号作者与个人贡献（新增版 5、20 页） | 保留三人学号作者；CONTRIBUTIONS.md | 已汇总，不重写旧历史 |
| 组长汇总提交（Other-Instructions.txt） | REPORT.md、SUBMISSION.md、提交 ZIP 与标签 | 本次准备提交版，未代上传 LMS |
| 相邻组仅按 README 复现（20 页） | [PEER_REVIEW_A11.md](PEER_REVIEW_A11.md) 与原始日志 | 已记录 B11 → A11 的实际尝试；A11 → B11 反馈未提供，不登记双向通过 |

资源差异：教师包默认 3.5 GiB 与胡博转述助教 2 GB 参考规格不同；B11 显式 b11-2gb 配置保留真实 1.7 GiB 和原阈值，原模式拒绝及适配模式成功均有证据。此次小型骨架运行通过不意味着 E5 以后所有负载都适用 2 GB。

不把组员运行或组长自动核验当作未发生的成员人工签字；A11 对 B11 的互评仍需实际反馈，报告与材料对此如实披露。
