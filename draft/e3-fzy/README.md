# fzy E3 失败与参考成功对照

本样本为 B11 手工基线，不是自动 DRAFT 的实现。固定源码：
`https://github.com/jhawthorn/fzy` 的 `28195b3a709995354b6c33cec9bb7c9f81532eb6`。

人工预期：

- broken：Ubuntu 基础环境未安装 make/C 工具链，构建非零退出，日志出现 `make: not found`。网络失败不算该预期故障。
- reference：安装 build-essential、Git、CA 后，同一源码构建退出 0，产生可执行 fzy；`make check` 的 31 测试通过、`./fzy --help` 退出 0。
- 功能断言：输入 `alpha\nbeta\n`，运行 `./fzy -e alp`，标准输出应精确为 `alpha\n`。依据是 fzy README 的模糊筛选语义和 `--help` 的 show-matches 说明。
- 独立容器使用 `--network none`，从干净构建重新验证；不运行需要 Ruby 的 acceptance 目标。

`run.py` 从已有 Git 克隆使用 `git archive` 导出固定提交，不复制工作区改动；保存源码清单、Dockerfile 与 diff、基础镜像 ID/digest、工具链、包清单、命令退出码和日志。运行目录及证据目录必须尚不存在。

在 B11 仓库根目录运行（Python 3.10+，Git/tar/Docker 可用）：

```bash
# 源码克隆不存在时才执行
git clone https://github.com/jhawthorn/fzy.git workspaces/draft-fzy
# 显式保留可 inspect 的基础镜像标签，BuildKit 缓存不一定创建标签
docker pull ubuntu:24.04
python3 draft/e3-fzy/run.py --source workspaces/draft-fzy --export-evidence e3/evidence/draft-sjy-新编号-fzy
```

Windows 可用 Python 3.11 调用；代理仅给当前进程设置，不能把 Windows 的 localhost 代理地址直接用于 WSL。脚本将本地基础镜像的 repo digest 作为 BASE_IMAGE 传给两个候选，固定同一次对照的基础镜像；APT 包版本仍未完全固定，结果代表记录的实际镜像环境。失败日志也保留，不覆盖旧目录。
