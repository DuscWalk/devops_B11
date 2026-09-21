# fzy 固定项目

| 项 | 选择 |
| --- | --- |
| 仓库 | https://github.com/jhawthorn/fzy |
| 完整 commit | `28195b3a709995354b6c33cec9bb7c9f81532eb6` |
| 选择原因 | 沿用 A11 已有 DRAFT 样例，C/Make 项目较小，源码内有独立测试目标 |
| 构建文件 | 仓库根目录 `Makefile`，不是 `src/Makefile` |
| 工作目录 | 源码根目录；容器候选内为 `/workspace/fzy` |
| 构建命令 | `make clean && make` |
| 验证命令 | `make check && ./fzy --help` |
| 配置提议 | `fzy-default-gcc13-make4.3`，待 A11 认可；不冒用原示例的 GCC10 配置 |

## 在 Linux / WSL 复现基线

需 Git、GCC、Make 和 libc 开发文件。以下命令在 B11 仓库根目录运行，克隆目标必须尚不存在：

```bash
git -c core.autocrlf=false clone https://github.com/jhawthorn/fzy.git workspaces/draft-fzy
git -C workspaces/draft-fzy checkout --detach 28195b3a709995354b6c33cec9bb7c9f81532eb6
cd workspaces/draft-fzy
git rev-parse HEAD
make clean && make
make check && ./fzy --help
```

本次实际由 Windows Git 克隆，在 WSL 构建；为消除 Windows/WSL 的换行识别差异，仅对该临时克隆设置了 `core.autocrlf=true`，未更改源码或全局配置。

2026-09-21 的真实日志见 `evidence/baseline-2026-09-21/`。两条命令均退出 0，31 个测试通过、99 个断言。编译存在上游 `asprintf` 返回值未使用警告，日志原样保留。未运行需要 Ruby/bundler 的 `acceptance` 目标；`make check` 不能代表全部测试覆盖。

本项目是构建环境准备样本，尚未证明其中含有可修复的 MD。MDFixer 固定报告由对应负责人另行准备。

## Docker 候选的下一步

`draft/Dockerfile` 是手工候选，用于后续对照 DRAFT 的生成结果。基础镜像 tag、APT 包未固定到 digest/版本，因此尚非完全可复现环境。

Docker Linux 引擎可用后，在仓库根目录执行：

```bash
docker build --platform linux/amd64 -t b11/fzy:28195b3-baseline -f draft/Dockerfile draft
docker run --rm b11/fzy:28195b3-baseline sh -lc 'make clean && make && make check && ./fzy --help'
docker image inspect b11/fzy:28195b3-baseline
```

这些 Docker 命令本次未执行。成功后记录镜像 ID、工具版本、真实日志，再决定使用注册表推送还是 `docker save`/`docker load` 交付。不得把演示文件中的 tag 当作已发布镜像。
