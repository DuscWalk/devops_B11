# E4 提交版交接

2026-10-21。三人的个人运行证据已经接收，不需要因为旧版待办文字重复完整实验。当前进度以 [STATUS](STATUS.md) 为准，个人归档 README 保留其原日期。

## 给组长

1. 提交入口为 [SUBMISSION.md](SUBMISSION.md)，报告为 [REPORT.md](REPORT.md)，贡献为 [CONTRIBUTIONS.md](CONTRIBUTIONS.md)。main 和标签 e4-b11-submission-20261021 对应本轮提交版。
2. 王硕与另外两人的完整源码 SHA 不同，但运行代码相同；直接使用 [COMPARISON.md](COMPARISON.md) 说明，不改原日志。
3. 组员已有的独立运行、密钥负向检查和对照都已归档。A11 对 B11 的反馈及成员未登记的逐项人工审阅不可填为已完成。
4. 用户授权合并和推送不等于已经上传 LMS；最终按平台要求由组长统一提交。

## 相邻组交接

B11 对 A11 固定提交的检查见 [PEER_REVIEW_A11.md](PEER_REVIEW_A11.md)，可将该文件交给 A11 说明实际问题。尚未收到 A11 对 B11 的反馈：将本仓库地址、提交标签和 README 交给对方，请其仅按操作说明复现，并返回执行人、日期、完整 SHA、命令、结论和日志位置。两种方向独立记录；本次没有代发组间消息。

新复现参见 [README](README.md)，固定提交标签后运行 make all。既有镜像和构建缓存保留，使用自己的学号身份和目录，不清理其他成员的镜像。
