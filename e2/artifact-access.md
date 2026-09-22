# E2 产物访问约定

确认依据见 AGREEMENT。URI 格式为 `artifact://<group>/<job_id>/<name>`；消费方映射为 `$ARTIFACT_ROOT/<group>/<job_id>/<name>`。E2 通过目录或归档交换，接收方根目录可以不同；相同目录名不意味着文件已同步。

## 三种实际样本

| 内容 | 根目录 / 元数据 |
| --- | --- |
| 初始文本演示 | fixtures/e2-handoff/artifacts；同目录上一级 artifact.json |
| DRAFT 的 5 个文件 | fixtures/draft-handoff/artifacts；draft/examples/query-succeeded.example.json 的 output.artifacts |
| MDFixer 的 3 个实际产物 | e2/evidence/mdfixer-2026-09-22/artifacts；同目录上一级 response.json 的 output.artifacts |

从仓库根目录：

```bash
python3 e2/artifact_access.py --root fixtures/e2-handoff/artifacts --metadata fixtures/e2-handoff/artifact.json
.venv/bin/python e2/validate.py
```

第一条读取初始 251 字节文件；统一校验直接用相同读取器消费 DRAFT 5 份和 REPAIR 3 份元数据并校验全部摘要。MDFixer 输出目录本身是 ARTIFACT_ROOT，内部按 b11/job_id/ 存储。

## 元数据和失败

artifact_id、type、uri、media_type、producer_job_id 必填；commit/configuration_id 用于追溯。本次所有交接文件都提供真实 sha256；共享 Schema 仍允许日志等未带摘要，若存在则必须匹配。关键补丁/图建议带摘要。读取器拒绝缺文件、摘要不匹配、缺媒体类型、路径越界；不会静默把 artifact URI 当任意本地路径。

产物在实验期间保留；清理需双方协调。文件类型取 media_type。HTTP 下载端点在 OpenAPI 中仅作后续接口说明，E2 没有部署。

## 镜像与报告

IMAGE 产物是镜像引用 JSON，不是镜像本体；DRAFT 的示例标记 example_only/NOT_BUILT。真实基线另在 draft/evidence，状态 LOCAL_DOCKER_ENGINE_ONLY。后续 docker save/load 需要单独传 tar、摘要和镜像 ID，实际接收后才能标可用。

人工 MDFixer ERROR_REPORT 位于 fixtures/mdfixer-project/artifacts。声明 MANUAL、固定独立源码提交与 Makefile 位置；不冒充 A11 实际检测报告。

本组已执行读取，不代表 A11 端已读取。A11 真实接收/执行证据在 E3 补录，当前接口确认与真实运行的区别见 STATUS。
