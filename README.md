# DevOps B11 · E2 接口契约 / E3 测试基线 / E4 可重复环境

B11：孙静怡负责 DRAFT，王硕负责 MDFixer，胡博负责公共接口与联调。配对组 A11 负责 BuildChecker、EChecker。

**E2 提交入口：[e2/README.md](e2/README.md)。LMS 填写说明：[e2/SUBMISSION.md](e2/SUBMISSION.md)。**

2026-09-22，胡博明确确认 A11 已认可前序接口方案；确认来源和范围见 [AGREEMENT.md](e2/AGREEMENT.md)。三人分支保留提交历史并合入交付版本。正式 Schema、四类请求/响应、错误样例、产物、设计记录、贡献与验证结果已集中归档。

## E4 入口

本次实验见 [E4 操作与交接](e4/README.md)、[执行状态](e4/STATUS.md)、[两版 PPT 差异](docs/e4/PPT_COMPARISON.md)。服务器每位组员各自克隆同一源码 SHA，在本人学号身份下运行 `make all`。默认采用经说明的 B11 2 GB 配置，真实资源和原模板差异写入证据。

## E2 快速验证

需要 Linux/WSL、Python 3.10+、Git、Make 和 C 编译器。仓库根目录运行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r e2/requirements.txt
.venv/bin/python e2/validate.py
```

当前 WSL 已配置 `.venv`。无 ensurepip 的环境按 [E2 环境说明](e2/README.md) 安装。统一校验会验证四类契约、反例、26 个回归检查，读取 DRAFT/MDFixer 产物，并在临时目录复现一次本地修复；不需要 Docker 或外部 API。

## 材料与实现

| 目录 | 内容 |
| --- | --- |
| [docs/](docs/README.md) | E2/E3 原课件、逐页文字、要求和来源摘要 |
| [e3/](e3/README.md) | 当前基线、统一验收、环境提案、证据与组员交接 |
| [e2/](e2/README.md) | 正式契约、OpenAPI、ADR、Backlog、确认、贡献、AI 使用、状态和证据 |
| [draft/](draft/README.md) | DRAFT 输入输出、5 个交接文件、固定 fzy 版本、手工 Docker 基线及执行日志 |
| [mdfixer/](mdfixer/README.md) | MDFixer 本地原型、固定人工 MD 报告、补丁及验证演示 |
| [fixtures/](fixtures/README.md) | 小型可交换文件、包含完整提交的源码 bundle 和来源说明 |

E2 不要求部署 API。DRAFT 自动生成迭代、真正镜像交付、A11 检测器重检和四服务端到端联调属于后续工作，具体限制见 [STATUS.md](e2/STATUS.md)。

## E3 快速验收

```bash
.venv/bin/python e3/scripts/run_baseline.py
# Docker 可用时独立执行
.venv/bin/python e3/scripts/verify_docker.py
```

E3 准备独立测试基线；自动 DRAFT、MDFixer 实现扩展和真实数据联调按 E5、E8、E12 推进。当前结果见 [e3/STATUS.md](e3/STATUS.md)。
