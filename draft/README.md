# DRAFT 阶段准备

范围：E2 输入输出审阅与 E3 样本准备。DRAFT 自动生成/迭代服务尚未实现，未部署 API。

## 已完成的本地工作

- 选定 fzy 的完整提交，核对根目录 Makefile 与构建命令。
- 在 WSL Ubuntu 24.04、GCC 13.3.0、Make 4.3 中完成构建、31 个上游测试及帮助命令验证。
- 准备请求、成功/失败响应和可读取的演示产物，并补充 Q03/Q07 建议。
- 手工 Dockerfile 已构建为本地镜像，独立容器断网重建与 31 个测试通过；镜像尚未发布或交付 A11。

## 文件入口

| 文件 | 用途 |
| --- | --- |
| [PROJECT.md](PROJECT.md) | 项目、版本、复现命令与 Docker 候选验证步骤 |
| [CONTRACT_REVIEW.md](CONTRACT_REVIEW.md) | 给接口负责人胡博的 Q03/Q07 审阅建议，待 A11 确认 |
| [examples/](examples/) | DRAFT 请求、202、成功/失败查询响应与来源信息 |
| [Dockerfile](Dockerfile) | 手工编写、已在本机验证的基线环境 |
| [交接样例](../fixtures/draft-handoff/README.md) | image_ref、迭代记录、验证结果和日志文件 |
| [真实执行结果](evidence/baseline-2026-09-21/result.json) | 本次 WSL 执行环境、命令、时间、退出码 |
| [真实镜像信息](evidence/docker-2026-09-21/image_ref.json) | 本地镜像 ID、大小、源码版本与交付状态；同目录保存 Docker 构建/验证日志 |
| [WORK_RECORD.md](WORK_RECORD.md) | 本分支进度、AI 辅助记录、未完成项 |

## 样例检查

在仓库根目录执行，需 Python 3.10+ 与 `jsonschema>=4.10,<5`：

```bash
python3 draft/validate_examples.py
```

校验器通过 Git 读取固定契约来源提交，不合并或修改组员分支。如本机没有来源对象，先 `git fetch origin`；也可使用 `--schema /path/to/task.schema.json` 指定来源文件，摘要必须与当前参考版本一致。

本次 WSL 使用已有 jsonschema 4.10.3；上游项目的构建不依赖该 Python 包。

所有 `job-draft-example` 产物均为人工构造的接口样例。成功响应不代表已运行 DRAFT 或已产出镜像。真实执行证据仅在 `evidence/` 中。
