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

## Docker 基线验证

`draft/Dockerfile` 是手工候选，用于后续对照 DRAFT 的生成结果。基础镜像 tag、APT 包未固定到 digest/版本，因此尚非完全可复现环境。

在仓库根目录执行：

```bash
docker build --platform linux/amd64 -t b11/fzy:28195b3-baseline -f draft/Dockerfile draft
docker run --rm --network none b11/fzy:28195b3-baseline sh -lc 'make clean && make && make check && ./fzy --help'
docker image inspect b11/fzy:28195b3-baseline
```

2026-09-21 已完成镜像构建及独立容器验证，均退出 0；独立容器禁用网络，核对固定源码 SHA 后重新构建，31 个测试通过、99 个断言，帮助命令退出 0。镜像为 `b11/fzy:28195b3-baseline`，ID、大小、工具链与完整包清单见 `evidence/docker-2026-09-21/`。上游编译警告原样保留，仍未运行 Ruby acceptance 目标。

该镜像只在当前 Docker daemon 中存在，未发布注册表、未导出归档、未由 A11 获取。后续与 A11 确认注册表或 `docker save`/`docker load` 交付方式。`fixtures/draft-handoff` 中的 contract-example tag 仍是人工演示，不是这个真实镜像。

### Docker Hub 网络问题的处理

2026-09-21 启动 Docker Desktop 后，第一次构建在获取 `auth.docker.io` 匿名令牌时连接超时，尚未进入编译。Windows 已启用 `127.0.0.1:7897` 代理，经该代理访问认证服务返回 HTTP 200。

重试时只在启动 Docker build 的子进程环境中设置 `HTTP_PROXY`、`HTTPS_PROXY` 为 `http://127.0.0.1:7897`，Ubuntu 镜像拉取恢复。没有更改系统代理或 Docker 全局配置。此端口属于本机现有配置，其他机器应使用自己的有效代理；不要把宿主机的 `127.0.0.1` 直接写入 Dockerfile。

首次失败日志与重试结果保存在 `evidence/docker-2026-09-21/`。
