# DevOps B11 · E2 接口契约 / E3 测试基线 / E4 可重复环境 / E5 论文复现 / E6 MVP

B11：孙静怡负责 DRAFT，王硕负责 MDFixer，胡博负责公共接口与联调。配对组 A11 负责 BuildChecker、EChecker。

**E2 提交入口：[e2/README.md](e2/README.md)。LMS 填写说明：[e2/SUBMISSION.md](e2/SUBMISSION.md)。**

2026-09-22，胡博明确确认 A11 已认可前序接口方案；确认来源和范围见 [AGREEMENT.md](e2/AGREEMENT.md)。三人分支保留提交历史并合入交付版本。正式 Schema、四类请求/响应、错误样例、产物、设计记录、贡献与验证结果已集中归档。

## E6 入口

**E6 审阅入口：[复现说明](e6/README.md)、[实验报告](e6/REPORT.md)、[要求核对](e6/REQUIREMENTS_CHECK.md)、[提交说明](e6/SUBMISSION.md)。分支：`feat/e6-submission`。**

B-DRAFT 的 CLI 自动完成初始缺 make 失败、候选构建及同一镜像 ID 的禁网验证。新增候选约束测试，重新构建后 25 项单测和课程门禁通过；源码与报告字段对照、原始日志及来源分别归档。课件见 [docs/e6](docs/e6/README.md)。

## E5 入口

**E5 提交入口：[提交说明](e5/SUBMISSION.md)、[小组报告](e5/REPORT.md)、[要求核对](e5/REQUIREMENTS_CHECK.md)。固定标签：`e5-b11-submission-20261102-r2`。**

已接收孙静怡的 E5 分支及王硕的独立复跑、交叉检查记录。孙静怡完成初始缺 make 失败、两类提示与候选、候选选择和换源调整、实际构建及同一镜像 ID 的禁网运行；王硕回放组内已有候选并核对两人的结果。胡博汇总并核验原始证据；来源与个人贡献分别保留。本次按 E5 课件第 19 页提交，E6 自动服务及 E7 测试、GitHub CI 与合并门禁属于后续阶段。复现步骤见 [E5 README](e5/README.md)，原课件见 [docs/e5](docs/e5/README.md)。

## E4 入口

**E4 提交入口：[提交说明](e4/SUBMISSION.md)、[实验报告](e4/REPORT.md)、[三人贡献](e4/CONTRIBUTIONS.md)。固定标签：`e4-b11-submission-20261021`。**

三人的运行日志和对照已整合：单测各 4/4，冒烟与密钥扫描通过；B11 对 A11 的 README 复现记录见 [互评记录](e4/PEER_REVIEW_A11.md)，尚未收到 A11 对 B11 的复现反馈。操作见 [E4 README](e4/README.md)，实际所测 SHA 差异见 [对照说明](e4/COMPARISON.md)，当前状态见 [STATUS](e4/STATUS.md)。默认采用经说明的 B11 2 GB 配置，真实资源和原模板差异写入证据。

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
| [docs/](docs/README.md) | E2–E6 原课件、逐页文字、教师实验包及来源摘要 |
| [e6/](e6/SUBMISSION.md) | E6 自动构建、程序验证、扩展测试、原始证据与报告 |
| [e5/](e5/SUBMISSION.md) | E5 提交报告、模型候选、手工构建与运行证据 |
| [e4/](e4/SUBMISSION.md) | E4 提交报告、三人证据、版本对照与贡献 |
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
