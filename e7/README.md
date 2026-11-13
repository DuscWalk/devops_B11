# B11 E7：测试、CI 与合并门禁

**当前状态：技术验证与 DRAFT 场景审阅已完成；CI 交叉验收和最终整合待完成，尚未形成最终提交版。** 审阅基线为 `review/e7-handoff`，个人审阅在 `review/e7-draft-241250112`。

E7 的审阅入口：[状态](STATUS.md)、[组员交接](HANDOFF.md)、[孙静怡 DRAFT 审阅](reviews/241250112-DRAFT.md)、[成员贡献](CONTRIBUTIONS.md)、[实验报告](REPORT.md)、[要求核对](REQUIREMENTS_CHECK.md)、[验收记录](验收记录.csv)、[审阅说明](REVIEW.md)。课程原件及逐页文字见 [docs/e7](../docs/e7/README.md)。

B 轨道要求的六项检查、正常/失败/恢复 CI、main 保护、实际拒绝合并及同一 PR 修复后合并已有真实证据。本次整理保留原始日志，并把此前混在 E5–E7 材料中的 E7 要求单独列出。课程实现仍在 `e5/labs/B-draft/`，工作流入口现为 `.github/workflows/e7-quality-gate.yml`，必需检查始终为 `e7-b-quality-gate`。

## 核验已有证据

从仓库根目录执行，Python 3.10+，无需 Docker 或第三方包：

```bash
python3 e7/scripts/verify_archive.py
```

该命令检查摘要、六项场景、CSV/JSON、超时清理记录、提交对应关系和分支保护快照；不将历史 CI 记为新运行。证据清单见 [evidence-manifest.json](evidence-manifest.json)。

## 重新运行

GitHub push 或 PR 会自动执行构建、扫描、单测及五个实际工作流场景，并始终上传 `work/ci/`，保留 14 天。CI 使用课程已保存的 `DeepSeek-E5.Dockerfile` 候选，没有在线模型调用。

在具备 Docker 的 Linux 主机也可执行以下整块命令。使用新目录保留每次日志，若失败先查看原始构建日志、网络与下载情况。

```bash
(
set -eu
cd e5/labs/B-draft
mkdir -p work
e7_run_dir=$(mktemp -d "$PWD/work/e7-own-XXXXXXXX")
e7_service_tag="e7-draft:$(basename "$e7_run_dir")"
docker build --progress=plain -f services/draft/Dockerfile -t "$e7_service_tag" .
python3 scripts/run_e7_b_gate.py --image "$e7_service_tag" \
  --candidate fixtures/ci-candidates/DeepSeek-E5.Dockerfile \
  --out "$e7_run_dir/gate" --build-timeout 600
cat "$e7_run_dir/gate/results.csv"
)
```

CI 在 GitHub 托管 runner 执行；此前学院 2 GB 主机的成功记录不变。课程通用 doctor 的 4 GiB 检查失败也保留，不能将它写成通过。
