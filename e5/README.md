# B11 E5：DRAFT 论文流程复现

更新：2026-11-02（北京时间）。孙静怡（241250112）授权 Codex 在本人服务器目录完成 B 轨道 E5：真实缺 make 故障、两类提示及本会话候选、候选选择与调整、实际构建及按镜像 ID 断网运行。详见 [个人报告](SUN_JINGYI_REPORT.md) 和 [证据入口](evidence/sun-jingyi-20261102/README.md)。

小组提交入口：[SUBMISSION.md](SUBMISSION.md)、[小组报告](REPORT.md)、[E5 要求核对](REQUIREMENTS_CHECK.md)、[贡献记录](CONTRIBUTIONS.md)。提交标签为 `e5-b11-submission-20261102-r2`；完整 SHA 通过 `git rev-parse e5-b11-submission-20261102-r2^{commit}` 取得。

| 检查 | 结果 |
| --- | --- |
| 初始构建 | Docker build 退出 1，日志含 `make: not found`，该 RUN 层退出 127 |
| 提示与候选 | 错误驱动、上下文驱动提示均由本次失败日志生成；两份候选和原始代码块已保存 |
| 候选构建 | 首次因下载无新进展主动中止（130）；单独记录镜像源调整后构建成功（0） |
| 实际程序 | 运行成功构建的完整 image ID，禁网，退出 0，精确输出 `hello E3\n`，容器已删除 |
| 来源与差异 | 教学参考代码原样执行；提示/候选/后续操作调整分开记录；不是论文原项目全集实验 |
| 资源自检 | **未通过**：新包要求 4 GiB，本机 1.7 GiB；未修改要求或将自检记为通过 |

E5 小样例技术流程已实际完成。胡博授权接收本分支并进行提交整合，归档摘要、课程源码、提示与回复、构建日志及镜像 ID/输出均已核验。学院分配的 2 GB 主机实际完成本次实验；保留原始 doctor 内存检查失败记录，不把该项写成通过，也不修改原日志。自动核验不登记为成员逐项人工签字。

E6 自动候选构建服务、E7 故障门禁/新增测试/GitHub CI 不属于这次执行范围，不能用本页记录登记为完成。

## 代码和材料来源

- 课程包：`DevOps_20261020_Course/02_学生实验/DevOps_1020_Student_Cloud.zip`，SHA-256 见证据中的 `source/course-source.json`。
- 使用 B 轨道参考 `scripts/lab_cloud.py e5` 与 `prepare_e5_prompts.py`；未改参考代码。
- 个人分支归档了实际使用的脚本/fixture 快照及新运行记录；组级提交另保存 [课程原件](../docs/e5/README.md)，用于核对来源，包内教师演示证据不计为本组结果。
- 原有 E2/E3/E4 不被新实验替换。原始贡献分支为 `feat/e5-draft-reproduction`，提交 `3e6573ab13dd51f6dd101113c045c0285093eae8`；组级交付使用 GitLab `main` 与上述标签。

## 复现 E5

在有 Docker 的 Linux 云主机中，从仓库根目录执行以下整块命令。它先重新采集失败和提示，再回放已保存的最终候选；不会产生新的模型回复。输出写入新的 `work/` 目录，不覆盖归档证据。

```bash
(
set -eu
archive="$PWD/e5/evidence/sun-jingyi-20261102"
mkdir -p work
trial=$(mktemp -d "$PWD/work/e5-reproduce-XXXXXXXX")
cp -R "$archive/source/." "$trial/"
mkdir "$trial/candidate"
cp "$archive/candidates/context-driven-mirror/Dockerfile" "$trial/candidate/Dockerfile"
cd "$trial"
printf 'E5_WORK_DIR=%s\n' "$trial"

if python3 scripts/lab_cloud.py e5 --out work/e5-01 --build-timeout 600 > driver.log 2>&1; then
  printf '0\n' > driver-exit-code.txt
else
  code=$?
  printf '%s\n' "$code" > driver-exit-code.txt
  cat driver.log
  exit "$code"
fi

image_tag="course1020-draft-e5:$(basename "$trial")"
if docker build --progress=plain -f candidate/Dockerfile -t "$image_tag" work/e5-01/project > candidate-build.log 2>&1; then
  printf '0\n' > candidate-build-exit-code.txt
else
  code=$?
  printf '%s\n' "$code" > candidate-build-exit-code.txt
  cat candidate-build.log
  exit "$code"
fi
docker image inspect "$image_tag" > image.json
image_id=$(docker image inspect "$image_tag" --format '{{.Id}}')
printf '%s\n' "$image_id" > image-id.txt
if docker run --rm --network none "$image_id" > verify.log 2> verify-stderr.log; then
  printf '0\n' > verify-exit-code.txt
else
  code=$?
  printf '%s\n' "$code" > verify-exit-code.txt
  exit "$code"
fi
printf 'hello E3\n' > expected-output.txt
cmp expected-output.txt verify.log
printf 'E5_REPLAY=PASS\n'
)
```

初始 `docker build` 应为 1，日志含 `make: not found`；E5 驱动采集成功应为 0。候选构建和运行均应为 0，stdout 应精确匹配 `hello E3\n`。如果初始失败发生在拉取或下载阶段，应先解决网络问题，不能将它当作缺 make 的目标失败。

## 第二名执行人：王硕（241250110）

2026-11-02 王硕在本人服务器目录独立完成同一 B 轨道 E5：真实缺 make 失败、两类提示、三份候选对照与选择、候选构建及按同一镜像 ID 断网运行。个人记录见 [王硕报告](WANG_SHUO_REPORT.md)，证据入口 [e5/evidence/wang-shuo-20261102/](evidence/wang-shuo-20261102/)，全量摘要 `SHA256SUMS.txt`（63 个文件），同一份记录另存于 GitHub 组仓库 `DuscWalk/devops_B11`。

| 检查 | 结果 |
| --- | --- |
| 初始构建 | Docker build 退出 1，日志含 `make: not found`，该 RUN 层退出 127（原始 stdout/stderr 已归档） |
| 提示与候选 | 两类提示由本次失败日志生成；三份候选（包内 DeepSeek、组内错误驱动、组内上下文驱动）与来源记录已保存 |
| 候选构建 | 选上下文驱动候选（仅调整 Debian 镜像源），`candidate-build-02` 退出 0，镜像 ID `sha256:49dc498e…ed6d` |
| 实际程序 | 同一完整 image ID 禁网运行，`verify-02` 退出 0，stdout 精确为 `hello E3` 换行，容器已删除 |
| 服务单测 | `build-02-mirror` 构建退出 0，`pytest` 退出 0，26 passed（课程 24 项 + B11 自定义 2 项） |
| 资源自检 | **未通过**：新包要求 4 GiB，本机 1.7 GiB；未修改要求或将自检记为通过 |
| 交叉核对 | 与孙静怡 241250112 的候选、日志逐项核对：基础 digest、失败原因、运行输出一致；镜像源主机与指令顺序不同，镜像 ID 不同属预期 |

补充提交修正了首次提交的三处记录问题：`.gitignore` 忽略 `*.log` 导致日志漏传（已强制加入）；退出码文件被写成 `True` / `0n`（已按日志核实改写为 `0`）；摘要清单只覆盖 7 个文件（已改为覆盖全量 63 个文件的 `SHA256SUMS.txt`）。

E6/E7 不在王硕本次分工范围，本页不登记为完成。
