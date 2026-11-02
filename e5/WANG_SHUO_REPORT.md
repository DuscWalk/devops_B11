# E5 B 组复现说明：王硕（241250110）

- 学号 / 姓名：241250110 / 王硕
- 轨道：B（DRAFT）
- 服务器：Huawei Cloud ECS 119.3.234.250，Ubuntu 22.04.5，2 vCPU，可见内存约 1.7 GiB，无 swap
- 组级仓库：<https://git.nju.edu.cn/devops_b11/devops-project-b11>（分支 `feat/e5-draft-reproduction`）；另在 <https://github.com/DuscWalk/devops_B11> 保留同一份 E5 记录
- 运行源码提交（GitHub 侧）：`ff447978ba0ffb2f12e6cc45616e174a3d6faeb2`
- 工作目录：`/root/241250110/e5-b11/e5/labs/B-draft`
- 证据归档：`e5/evidence/wang-shuo-20261102/`
- 全量摘要：`SHA256SUMS.txt`（覆盖归档内除自身外全部 63 个文件）
- 运行时间：2026-11-02；补充归档 2026-11-02 晚

## 1. 前置：环境自检与服务构建

`python3 scripts/lab_cloud.py doctor`（原始输出见 `doctor.txt`）：Docker 29.1.3、Compose、Buildx、git、make、python3 均可用；`problems` 只有一项 `mem_gib=1.7 低于最低要求 4`。本机为学院分配的 2 GB 机型，与孙静怡记录的限制相同；本次按实际规格继续实测，结论不外推到更大规模。

服务构建：课程原始 `services/draft/Dockerfile` 使用官方 Debian 源，本机下载 9.6 MB 索引 10 分钟无进展（`deb.debian.org` 实测极慢）。改按组内既有做法，用同 digest 的镜像源适配基础层 `e5-python-base:mirror`（华为 HTTPS Debian 源 + 华为 PyPI 源）作为 `BASE_IMAGE` 构建参数，课程 Dockerfile 与依赖锁文件未改动。

- `build-01-mirror/`：首次构建，输出合并记录（历史保留）
- `build-02-mirror/`：**本次正式记录**，stdout 与 stderr 分流保存

正式记录结果：构建 `exit_code=0`（`build-02-mirror/build/exit-code.json`、`stdout.log`、`stderr.log`），镜像 ID `sha256:f46dfb0a801b622738fe3a71a5e7ab33a9a0e41c25b2736e7852004ca7562c81`；`--network none` 下 `pytest` 为 `exit_code=0`，**26 passed**（课程 24 项 + B11 自定义 2 项），日志与退出码在 `build-02-mirror/unit-tests/`。

## 2. 初始失败基线

`python3 scripts/lab_cloud.py e5 --out work/e5-01 --build-timeout 1200`，采集入口退出 0（预期失败已归档，`e5-01/e5-exit-code.txt` = 0）。

本次初始输入 `e5-01/iter-01/Dockerfile`（FROM 已统一为候选固定 digest）：

```dockerfile
FROM python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN make
CMD ["./hello"]
```

真实构建输出（原始日志在 `e5-01/iter-01/build/` 与 `build-retry.log`）：

- `/bin/sh: 1: make: not found`（出现 2 次）
- 该 RUN 层退出 127，外层 docker build 退出 1
- `e5-01/iter-01/build/exit-code.json`：`{"exit_code": 1}`；`result-retry.json` 记录 `build_exit_code: 1`

失败原因与 `Makefile` 对应：`hello: main.c` 需要 C 编译器与 GNU Make，而 `python:3.13-slim` 不含 make。

## 3. 两类提示

- 错误驱动：`e5-01/iter-01/prompt-error-driven.txt`（Dockerfile + 真实失败日志）
- 上下文驱动：`e5-01/iter-01/prompt-context-driven.txt`（额外给出 README：需要 C 编译器与 GNU Make，输出必须为 `hello E3`）

两份提示均由本次真实失败日志生成，不是改写过的日志。

## 4. 候选与选择

本次为课堂记录候选路线，三个候选及来源记录见 `e5-01/candidate-0*/`：

| 候选 | 来源 | 要点 | SHA-256（Dockerfile） |
|---|---|---|---|
| candidate-01 | 课程包内已保存 DeepSeek 候选（`fixtures/ci-candidates/`，注明来源） | 保留 digest；`apt-get install build-essential`；官方 Debian 源 | `ede21b0f…535d` |
| candidate-02 | 组内已保存 Codex 错误驱动回复（2026-10-29） | 保留 digest；安装 `gcc make libc6-dev`；官方 Debian 源 | `7daf10bd…77fd` |
| candidate-03 | 组内已保存 Codex 上下文驱动回复（2026-10-29） | 保留 digest；`build-essential`；改华为 HTTPS Debian 源 | `6c1408e3…70d1` |

**复跑对象说明**：本次候选来自组内 2026-10-29 保存的模型回复（回放已有记录），不是本次现场新生成；提示由本次失败日志重新生成。孙静怡 2026-11-02 的候选为她本人在她目录新生成的回复，两者来源不同，因此不把她的候选直接当作我的候选使用，只做交叉核对（见第 7 节）。

选择过程按 R1—R4：

- R1：三个候选均未在本轮构建过镜像，保留。
- R2：三者方案一致（补装 C 构建工具），差异仅在包名与 apt 源；续行按 Dockerfile 折行归一化后比较。
- R3：三者都含失败相关核心关键词 `make` 与 C 编译器（`build-essential` / `gcc`），均满足。
- R4：本机实测官方 Debian 源不可用，因此选 **candidate-03**：保留固定 digest、`WORKDIR`、`COPY`、`RUN make`、`CMD`，仅把 apt 源换成华为 HTTPS 镜像，属网络环境适配，不改变项目与构建语义。

人工修改：无（candidate-03 即组内保存的原始候选内容）。

## 5. 候选构建与同一镜像验证

```bash
docker build --progress=plain -f work/e5-01/candidate-03/Dockerfile \
  -t course1027-e5-candidate:241250110 work/e5-01/project
```

- 构建 `exit_code=0`，stdout/stderr 分流保存在 `e5-01/candidate-build-02/`，末尾 stderr 含 `naming to … done`
- 镜像 ID：`sha256:49dc498ec1cb1984f45c54ddd167d27825f4d892fb8f6e108485206f2b47ed6d`（`candidate-build-02/image-id.txt`）
- 同一完整镜像 ID、禁网、受限资源运行：

```bash
docker run --rm --network none --cpus 1 --memory 256m --pids-limit 64 <image-id>
```

- `exit_code=0`（`e5-01/verify-02/exit-code.json`），stdout 精确为 `hello E3\n`，stderr 为 0 字节（`verify-02/stdout.log`、`stderr.log`），容器已删除

首次运行的合并日志保留在 `e5-01/candidate-build.log`、`e5-01/verify.log`，与 `*-02` 结论一致；`*-02` 为本次正式记录。

## 6. 与孙静怡（241250112）本次结果的交叉检查

| 项目 | 孙静怡 241250112 | 王硕 241250110 | 结论 |
| --- | --- | --- | --- |
| 基础镜像 | `python:3.13-slim@sha256:70729b46…` | 同一 digest | 一致 |
| 初始失败 | 缺 make，build=1 | 缺 make，build=1，该层 127 | 一致 |
| 选定候选 | `context-driven-mirror`：`repo.huaweicloud.com/debian`，apt 置于 WORKDIR 之前，带 `Acquire::Retries` 与超时参数 | `candidate-03`：`mirrors.huaweicloud.com`，WORKDIR 后 apt | 思路一致，镜像源主机与指令顺序不同 |
| 构建结果 | exit=0，耗时 88.75 s | exit=0 | 均通过 |
| 镜像 ID | `sha256:57dfd1ba…` | `sha256:49dc498e…` | 不同，原因是指令顺序与源 URL 不同，属预期 |
| 运行验证 | 断网、exit=0、`hello E3\n`、容器已清理 | 断网、exit=0、`hello E3\n`、`--rm` 已删除 | 一致 |
| 服务单测 | 未登记（其本次范围只做 E5 分步复现） | 26 passed（课程 24 + B11 自定义 2） | 范围不同，不互为矛盾 |
| 资源自检 | FAIL：1.7 GiB < 4 GiB | FAIL：1.7 GiB < 4 GiB | 一致，均未改写要求 |

交叉检查只用于核对结论是否互斥；两套证据各自出自本人目录与本人运行，未共用对方的日志或镜像。

## 7. 修正与补充记录

提交后自查发现三处记录问题，均已在本次补充中修正：

1. **日志漏传**：仓库 `.gitignore` 忽略 `*.log`，首次提交只带上了非日志文件，导致 `build-retry.log`、`candidate-build.log`、`verify.log` 及构建 stdout/stderr 缺失。本次对证据目录内全部日志执行强制加入，并新增 `build-02-mirror/`、`candidate-build-02/`、`verify-02/` 的分流 stdout/stderr 与退出码。
2. **退出码文件异常**：`build-01-mirror/build/exit-code.txt` 等文件曾被写成字面量 `True` / `0n`（采集时的转义问题），与日志不符。已按日志核实后改写为真实数值 `0`，并在 `build-02-mirror/` 中用新采集的退出码作为正式记录。
3. **摘要清单不全**：原 `e5-01/checksums.txt` 只覆盖 7 个文件，不能作为整包校验清单。已删除该文件，改为归档根目录 `SHA256SUMS.txt`，覆盖除自身外全部 63 个文件。

## 8. 文件对应

| 内容 | 路径 |
|---|---|
| 初始 Dockerfile / 失败日志 / 结果 JSON | `e5-01/iter-01/`（含 `build/stdout.log`、`build/stderr.log`、`build-retry.log`） |
| 两类提示 | `e5-01/iter-01/prompt-*.txt` |
| 三个候选、原始回复、来源记录 | `e5-01/candidate-0*/` |
| 候选构建（分流日志、退出码、镜像 ID） | `e5-01/candidate-build-02/`；首次合并日志 `e5-01/candidate-build.log` |
| 断网运行验证 | `e5-01/verify-02/`；首次合并日志 `e5-01/verify.log` |
| 服务构建与 26 项单测 | `build-02-mirror/`（正式）；`build-01-mirror/`（首次，历史保留） |
| 环境自检 | `doctor.txt` |
| 全量摘要 | `SHA256SUMS.txt` |

本次只覆盖课程包内 `hello E3` 微型样例，未运行论文数据集；E6/E7 不在本人本次分工范围内。
