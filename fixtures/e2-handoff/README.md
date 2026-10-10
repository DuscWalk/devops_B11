# E2 文件读取演示

本目录只演示“元数据 URI → 文件字节 → SHA-256 核验”。它由胡博的接口准备工作生成（Codex 辅助），没有运行任何论文工具。

- `artifact.json`：符合 A11 Artifact 定义的演示元数据，摘要来自实际文本文件。
- `artifacts/b11/job-e2-read-demo/handoff.txt`：251 字节的文本样本。
- `job-e2-read-demo` 是演示标签，不是服务执行记录；LOG 也不表示真实构建日志。

在仓库根目录执行：

```bash
python3 e2/artifact_access.py --root fixtures/e2-handoff/artifacts --metadata fixtures/e2-handoff/artifact.json
```

该命令只做本机读取；跨组运行由 A11/B11 协商后记录。该样本不替代王硕负责的 E3 固定 MD 报告。完整约定见 [artifact-access.md](../../e2/artifact-access.md)。
