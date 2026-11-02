# E5 B 组复现说明：王硕（241250110）

- 学号 / 姓名：241250110 / 王硕
- 轨道：B（DRAFT）
- 服务器：Huawei Cloud ECS 119.3.234.250，Ubuntu 22.04.5，2 vCPU，可见内存约 1.7 GiB，无 swap
- 组级仓库：<https://git.nju.edu.cn/devops_b11/devops-project-b11>（分支 `feat/e5-draft-reproduction`）；另在 <https://github.com/DuscWalk/devops_B11> 保留同一份 E5 记录
- 运行源码提交（GitHub 侧）：`ff447978ba0ffb2f12e6cc45616e174a3d6faeb2`
- 工作目录：`/root/241250110/e5-b11/e5/labs/B-draft`
- 证据归档：`e5/evidence/wang-shuo-20261102/`
- 运行时间：2026-11-02

## 1. 前置：环境自检与服务构建

`python3 scripts/lab_cloud.py doctor`（原始输出见 `doctor.txt`）：Docker 29.1.3、Compose、Buildx、git、make、python3 均可用；`problems` 只有一项 `mem_gib=1.7 低于最低要求 4`。本机为学院分配的 2 GB 机型，与孙静怡记录的限制相同；本次按实际规格继续实测，结论不外推到更大规模。

服务构建 `build-01-mirror`：课程原始 `services/draft/Dockerfile` 使用官方 Debian 源，本机下载 9.6 MB 索引 10 分钟无进展（`deb.debian.org` 实测极慢）。改按组内既有做法，用同 digest 的镜像源适配基础层 `e5-python-base:mirror`（华为 HTTPS Debian 源 + 华为 PyPI 源）作为 `BASE_IMAGE` 构建参数，课程 Dockerfile 与依赖锁文件未改动。构建退出 0，镜像 ID `sha256:d5a3ca49a0055fe48fc43ca5072c0bd397c8aa18333b1072e5638abef6b9e8b8`，`--network none` 下 `pytest` 得到 **26 passed**（课程 24 项 + B11 自定义 2 项）。

## 2. 初始失败基线

`python3 scripts/lab_cloud.py e5 --out work/e5-01 --build-timeout 1200`，采集入口退出 0（预期失败已归档）。

本次初始输入 `work/e5-01/iter-01/Dockerfile`（FROM 已统一为候选固定 digest）：

```dockerfile
FROM python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c Makefile ./
RUN make
CMD ["./hello"]
```

真实构建输出：

- `/bin/sh: 1: make: not found`（出现 2 次，见 `e5-01/iter-01/build-retry.log`）
- 镜像内命令退出 127，外层 docker build 退出 1
- `e5-01/iter-01/result-retry.json`：`{"build_exit_code": 1}`

失败原因与 `Makefile` 对应：`hello: main.c` 需要 C 编译器与 GNU Make，而 `python:3.13-slim` 不含 make。

## 3. 两类提示

- 错误驱动：`e5-01/iter-01/prompt-error-driven.txt`（Dockerfile + 真实失败日志）
- 上下文驱动：`e5-01/iter-01/prompt-context-driven.txt`（额外给出 README：需要 C 编译器与 GNU Make，输出必须为 `hello E3`）

两份提示均由本次真实失败日志生成。

## 4. 候选与选择

本次为课堂记录候选路线（模型交互记录由组内在 2026-10-29 保存，非现场新生成），三个候选及来源记录见 `e5-01/candidate-0*/`：

| 候选 | 来源 | 要点 | SHA-256（Dockerfile） |
|---|---|---|---|
| candidate-01 | 课程包内已保存 DeepSeek 候选（`fixtures/ci-candidates/`，注明来源） | 保留 digest；`apt-get install build-essential`；官方 Debian 源 | `ede21b0f…535d` |
| candidate-02 | 组内已保存 Codex 错误驱动回复（2026-10-29） | 保留 digest；安装 `gcc make libc6-dev`；官方 Debian 源 | `7daf10bd…77fd` |
| candidate-03 | 组内已保存 Codex 上下文驱动回复（2026-10-29） | 保留 digest；`build-essential`；改华为 HTTPS Debian 源 | `6c1408e3…70d1` |

选择过程按 R1—R4：

- R1：三个候选均未在本轮构建过镜像，保留。
- R2：三者方案一致（补装 C 构建工具），差异仅在包名与 apt 源；文本续行按 Dockerfile 折行原样归一化比较。
- R3：三者都包含失败相关核心关键词 `make` 与 C 编译器（`build-essential` / `gcc`），均满足。
- R4：本机实测官方 Debian 源不可用（9.6 MB 索引 10 分钟无进展），因此选 **candidate-03**：保留固定 digest、`WORKDIR`、`COPY`、`RUN make`、`CMD`，仅把 apt 源换成华为 HTTPS 镜像，属于网络环境适配，不改变项目与构建语义。

人工修改：无（candidate-03 即组内保存的原始候选内容）。

## 5. 候选构建与同一镜像验证

```bash
docker build --progress=plain -f work/e5-01/candidate-03/Dockerfile \
  -t course1027-e5-candidate:241250110 work/e5-01/project
```

- 构建退出码：0（`e5-01/candidate-build.log`）
- 镜像 ID：`sha256:ac301bae0dab6cca766ee9c888d459c5d2d5d0354e992d12500aff7bab96f1eb`（`e5-01/candidate-image-id.txt`）
- 同一完整镜像 ID、禁网、受限资源运行：

```bash
docker run --rm --network none --cpus 1 --memory 256m --pids-limit 64 <image-id>
```

- 退出码：0（`e5-01/verify-exit-code.txt`）
- 标准输出：`hello E3`（`e5-01/verify.log`，stderr 为空，容器已删除）

镜像构建成功与程序行为正确分别记录，均为通过。

## 6. 文件对应

| 内容 | 路径 |
|---|---|
| 初始 Dockerfile / 失败日志 / 结果 JSON | `e5/evidence/wang-shuo-20261102/e5-01/iter-01/` |
| 两类提示 | `e5/evidence/wang-shuo-20261102/e5-01/iter-01/prompt-*.txt` |
| 三个候选、原始回复、来源记录 | `e5/evidence/wang-shuo-20261102/e5-01/candidate-0*/` |
| 候选构建日志、镜像 ID、运行输出与退出码 | `e5/evidence/wang-shuo-20261102/e5-01/` |
| 服务构建与 26 项单测 | `e5/evidence/wang-shuo-20261102/build-01-mirror/` |
| 环境自检 | `e5/evidence/wang-shuo-20261102/doctor.txt` |
| 摘要校验 | `e5/evidence/wang-shuo-20261102/e5-01/checksums.txt` |

本次只覆盖课程包内 `hello E3` 微型样例，未运行论文数据集；E6/E7 不在本人本次分工范围内。
