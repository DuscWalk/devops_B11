# B11 E4 提交证据汇总（2026-10-21）

- [成员机器对照](member-comparison.json)：三位成员 62 份原始归档，旧摘要清单保留。
- [整合版云端运行](integration-run/README.md)：候选 SHA a5f489a686f349728dcd986926e0e170de414012，make all 通过。
- [E3 本地回归](e3-baseline/README.md)：67/67；另见 [扫描器回归](scanner-regressions.txt)，2/2。
- [B11 → A11 互评](../../PEER_REVIEW_A11.md)：首次过早中断已更正；原配置重跑因慢速下载触发自身 900 秒构建超时；保持 digest/依赖锁的换源诊断完整通过（9/9、冒烟和扫描）。A11 → B11 反馈未提供。
- [补充材料摘要清单](SHA256SUMS.json)：覆盖本目录内除该清单、member-comparison.json 和本说明以外的文件，避免自引用。原文证据不改写。

在完整 Git 克隆中执行 `python3 e4/verify_evidence.py`，核验原始文件、补充清单及运行代码版本。核验 PASS 指证据完整性和 B11 结果符合预期，不表示 A11 完整复现通过或已收到对方反馈。
