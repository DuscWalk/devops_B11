# DRAFT · B11 E2 / E3 基线

E3 最新进度（2026-10-10）：已完成公共基线复跑及 fzy 真实缺工具链/参考成功对照，见 [模块交接与证据](../e3/draft-notes.md)。可复跑的 fzy 入口见 [e3-fzy](e3-fzy/README.md)。

负责人孙静怡。接口方案由胡博于 2026-09-22 明确确认 A11 已认可，见 [AGREEMENT](../e2/AGREEMENT.md)。

已交付：固定 fzy 版本、构建/验证命令、DRAFT 请求/202/完整成功失败响应、5 个可读文件，WSL 和手工 Docker 基线日志。自动生成/迭代服务尚未实现。

| 入口 | 内容 |
| --- | --- |
| [PROJECT.md](PROJECT.md) | 完整源码 SHA、命令、根目录 Makefile、Docker 复现 |
| [CONTRACT_REVIEW.md](CONTRACT_REVIEW.md) | 9 月 21 日回复历史，后续确认以公共 AGREEMENT 为准 |
| [examples/](examples/) | 请求、缺验证命令反例、202 和查询 |
| [Dockerfile](Dockerfile) | 手工基线，基础 tag/APT 未锁版本 |
| [fixtures/draft-handoff](../fixtures/draft-handoff/README.md) | 人工接口产物，example_only，与真实执行证据区分 |
| [evidence/docker-2026-09-21](evidence/docker-2026-09-21/) | 本地镜像 ID、工具版本、构建和断网运行日志 |
| [WORK_RECORD.md](WORK_RECORD.md) | 原作者过程与 AI 记录，附当前状态 |

在仓库根目录运行：

```bash
.venv/bin/python draft/validate_examples.py
```

校验使用本仓库 e2/task.schema.json 及记录的摘要，ZIP 无需额外 Git 对象。胡博整合时保持内容样例不变，仅切换正式 Schema 和补强反例校验。

基线为 fzy `28195b3a709995354b6c33cec9bb7c9f81532eb6`，Ubuntu24.04/GCC13.3/Make4.3；make clean && make；make check && ./fzy --help。来源日志记录 31 测试、99 断言通过，Ruby acceptance 未运行。镜像仅在孙静怡的 Docker daemon，尚未交付 A11。人工成功样例不代表自动 DRAFT 执行。
