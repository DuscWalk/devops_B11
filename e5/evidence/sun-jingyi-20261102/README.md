# 241250112 E5 证据索引

日期：2026-11-02（北京时间）。执行人归属：孙静怡授权 Codex。服务器 `duscwalk` 用户，独立目录 `/home/duscwalk/241250112/e5-20261102`。报告见 [个人报告](../../SUN_JINGYI_REPORT.md)。

| 路径 | 内容 |
| --- | --- |
| [source/manifest.json](source/manifest.json) | 参考源码本地 SHA、干净状态、实际使用脚本和 fixture 摘要；同目录是源码快照 |
| [preflight/doctor.log](preflight/doctor.log) | 原始自检 FAIL：1.7 GiB 不满足 4 GiB；没有篡改成 PASS |
| [e5-01/iter-01/result-retry.json](e5-01/iter-01/result-retry.json) | 初始 build=1；build/ 记录命令与原始 stdout/stderr |
| [e5-01/iter-01/error-localization.json](e5-01/iter-01/error-localization.json) | 从本次实际日志抽取的错误与行号 |
| [错误提示](e5-01/iter-01/prompt-error-driven.txt)、[上下文提示](e5-01/iter-01/prompt-context-driven.txt) | 本次实际提示原文 |
| [错误候选](candidates/error-driven/provenance.json)、[上下文候选](candidates/context-driven/provenance.json) | 各自 Dockerfile、原始代码块、提示副本与来源；同会话生成，不是独立 API 调用 |
| [调整候选](candidates/context-driven-mirror/provenance.json) | 后续镜像源调整版，保留原回复路径及 adjustment.diff |
| [candidate-build-01/result.json](candidate-build-01/result.json) | 原候选下载无新进展后主动中止，exit=130，不计为成功 |
| [candidate-build-02/result.json](candidate-build-02/result.json) | 调整候选构建 exit=0；command.json、stdout.log、stderr.log 完整保存 |
| [verification/result.json](verification/result.json) | 按同一 image ID 断网运行，exit=0，精确输出 hello E3 换行 |
| [verification/cleanup-check.json](verification/cleanup-check.json) | 运行容器已清理的实际检查 |
| [verification/repair.diff](verification/repair.diff) | 初始 Dockerfile 与最终选定候选的差异 |
| [verification/secret-scan.txt](verification/secret-scan.txt) | 服务器参考仓库文件、历史及生成镜像扫描结果 |
| [REMOTE_SHA256SUMS.json](REMOTE_SHA256SUMS.json) | 服务器导出时的逐文件摘要；本地说明及核验结果另外记录 |

`context-driven/provenance.json` 的 selected=true 表示首次选择进行构建，最终成功选定的是其派生版本 `context-driven-mirror`；详见 [selection.json](selection.json)。原时间点的来源记录不改写。

## 使用已归档输入重现 E5 核心检查

在有 Docker 的 Linux 上，从本证据目录执行；在仓库忽略的 `work/` 中选一个全新目录，按本人的学号命名镜像。以下只演示已保存候选回放，不会产生新的模型回复：

```bash
trial="$PWD/../../../work/e5-replay-$(date -u +%Y%m%dT%H%M%S)-241250112"
mkdir -p "$trial"
docker build --progress=plain -f e5-01/iter-01/Dockerfile \
  -t e5-broken:241250112 e5-01/project > "$trial/broken.log" 2>&1
# 预期退出 1，broken.log 中必须实际出现 make: not found。
docker build --progress=plain -f candidates/context-driven-mirror/Dockerfile \
  -t e5-reference:241250112 e5-01/project > "$trial/reference.log" 2>&1
# 上一步退出 0 后才执行以下步骤。
image_id=$(docker image inspect e5-reference:241250112 --format '{{.Id}}')
docker run --rm --network none --cpus 2 --memory 1g --pids-limit 256 \
  "$image_id" > "$trial/verify.log" 2> "$trial/verify-stderr.log"
# 预期退出 0，verify.log 精确为 hello E3 加换行。
```

各次运行保留自己的退出码与日志，不用新结果覆盖本目录。正式 E5 提示生成入口和相关输入也在 `source/` 快照中；完整参考实验源码来自已标注摘要的课程 ZIP。不得把教师参考代码或本次 AI 辅助记录说成本人从零实现或独立人工审阅。
