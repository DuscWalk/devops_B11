# MDFixer · B11 本地原型

负责人王硕；胡博在 E2 提交整合时修复语法/接口和演示。适配 [公共提交契约](../e2/task.schema.json)，功能范围为显式简单 Makefile 规则的缺失依赖补丁；不是完整论文复现或已部署服务。

## 一键演示

仓库根目录（Python 3.10+、jsonschema、Git、Make、C 编译器）：

```bash
.venv/bin/python mdfixer/validate_examples.py
.venv/bin/python mdfixer/demo.py
```

演示从仓库内 project.bundle 克隆完整固定源码，不联网；读取明确标 MANUAL 的混合报告，仅修 app.o 缺少 config.h 声明，保留 legacy.h。验证补丁能应用、构建/测试通过、修改头文件后重编译。原型输出 PATCH、STYLE_REPORT、TEST_RESULT；重检标 NOT_RUN，未运行 A11 检测器。

保存新执行证据可用 `--evidence-dir /tmp/b11-md-evidence`；已提交的真实结果在 [e2/evidence/mdfixer-2026-09-22/](../e2/evidence/mdfixer-2026-09-22/)。

## 手动 CLI

先将 fixture bundle 克隆到独立工作区，再运行：

```bash
git clone fixtures/mdfixer-project/project.bundle /tmp/b11-md-project
.venv/bin/python mdfixer/mdfixer.py --local \
  --request mdfixer/examples/repair_request.json \
  --workspace /tmp/b11-md-project \
  --artifact-root fixtures/mdfixer-project/artifacts \
  --out-dir /tmp/b11-md-output > /tmp/b11-md-response.json
```

临时目标路径应未被占用。输出目录按 b11/job_id/name 存储，响应为完整 REPAIR Job。CLI 显式 --local 表示在当前主机运行请求内构建命令，**不会使用 input.image 启动容器**。工作区 HEAD、Makefile URI、报告 commit 必须对应，tracked 文件应干净。候选验证后恢复原 Makefile，最终补丁需另行应用。

## 模块

| 文件 | 职责 |
| --- | --- |
| mdfixer.py | Schema 校验、CLI、完整 Job 输出 |
| mdfixer_core.py | 数据模型、URI、报告解析和 MISSING/RESOLVED 过滤 |
| mdfixer_engine.py | 简单显式规则索引与风格特征 |
| mdfixer_patch.py | 添加声明、生成可应用 unified diff |
| mdfixer_verify.py | 限时命令、候选验证及原文件恢复 |
| mdfixer_runner.py | 版本匹配、候选流程、产物及统计 |
| validate_examples.py / demo.py / test_mdfixer.py | 标准契约检查、实际执行演示、6 个回归 |

## 支持边界

支持简单显式规则和续行，追加依赖时保留配方与已有 RD；变量展开、模式规则、多重同名目标、复杂 include 等不猜测修复。每个 finding 生成一个候选，不实现搜索迭代；max_iterations 仅保留契约字段。timeout_seconds 在当前原型限制每条构建/验证命令，不是整个任务总时限。构建成功不等同于工具重检，缺少重检时不返回伪造的 remaining=0。

来源初版为王硕 feat/mdfixer 97fb979；胡博整合修正保留 Git 追溯。原初版示例使用占位 SHA/无源码与不完整 Job，当前替换为可复现教学项目；人工来源和固定版本见 [fixture README](../fixtures/mdfixer-project/README.md)。
