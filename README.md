# DevOps B11 · E2 需求与接口契约

B11：孙静怡负责 DRAFT，王硕负责 MDFixer，胡博负责公共接口与联调。配对组 A11 负责 BuildChecker、EChecker。

**E2 提交入口：[e2/README.md](e2/README.md)。LMS 填写说明：[e2/SUBMISSION.md](e2/SUBMISSION.md)。**

2026-09-22，胡博明确确认 A11 已认可前序接口方案；确认来源和范围见 [AGREEMENT.md](e2/AGREEMENT.md)。三人分支保留提交历史并合入交付版本。正式 Schema、四类请求/响应、错误样例、产物、设计记录、贡献与验证结果已集中归档。

## 快速验证

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
| [e2/](e2/README.md) | 正式契约、OpenAPI、ADR、Backlog、确认、贡献、AI 使用、状态和证据 |
| [draft/](draft/README.md) | DRAFT 输入输出、5 个交接文件、固定 fzy 版本、手工 Docker 基线及执行日志 |
| [mdfixer/](mdfixer/README.md) | MDFixer 本地原型、固定人工 MD 报告、补丁及验证演示 |
| [fixtures/](fixtures/README.md) | 小型可交换文件、包含完整提交的源码 bundle 和来源说明 |

E2 不要求部署 API。DRAFT 自动生成迭代、真正镜像交付、A11 检测器重检和四服务端到端联调属于后续工作，具体限制见 [STATUS.md](e2/STATUS.md)。
