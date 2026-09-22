# A11 / B11 E2 确认记录

## 确认依据

2026-09-22，B11 接口负责人胡博说明“王硕已经更新了仓库，A11也已经确认”，并在询问确认范围后回复“没有原文。直接确认”。据此，将前序 E2 接口提议登记为已确认。没有补造 A11 联系人、聊天原文、具体会议时间、截图或签名。

A11 仓库在本轮核对时为 `8b0c3b9142cb379547e429e310c1b3b0bb9ccd34`，其过程文件尚未回填本次确认，四份核心契约文件与 96f35cc 相同。本文件的确认来源是胡博的明确确认，并非声称 A11 Git 文档已同步。

## 确认内容与落地

| 议题 | E2 采用的约定 | 落地位置 |
| --- | --- | --- |
| Q01 公共模型 | DRAFT/FULL_CHECK/INCREMENTAL_CHECK/REPAIR；沿用四个 POST 和 GET 查询；服务器生成 job_id，trace_id 贯穿流程；增量查询补齐 configuration_id | task.schema.json、contract-examples.json、openapi.yaml |
| Q02 产物读取 | artifact://group/job_id/name 映射到接收方 ARTIFACT_ROOT；E2 通过目录/归档交换小产物，携带摘要则必须匹配 | artifact-access.md、实际文件与读取器 |
| Q03 DRAFT | 固定 fzy SHA，根目录构建；make clean && make；make check && ./fzy --help；5 次/1800 秒；Ubuntu24.04/GCC13/Make4.3 候选 | draft/PROJECT.md、examples/ |
| Q04 MDFixer | 接收混合 MD/RD，消费方仅处理当前源码版本仍有效的 MISSING；忽略 REDUNDANT、RESOLVED；Makefile 明确定位 | mdfixer/、ErrorReport 定义、人工固定报告 |
| Q05 响应/错误 | 202 必含 job_id/job_type/QUEUED；查询返回完整 Job；执行失败空 output + error，正常发现进入 findings；无候选被接受可以是正常完成 | Schema 状态约束、完整失败样例 |
| Q06 幂等与重试 | 按 job_type + idempotency_key 标识请求；同键同输入复用任务，同键异输入返回 HTTP 409 + CONTRACT_4002；新执行使用新键；本地 CLI 不实现任务存储 | ADR、OpenAPI；服务实现列入 E3 |
| Q07 配置与版本 | 本环境标识 fzy-default-gcc13-make4.3；基线提交和配置必须匹配；保留 schema_version=1.1.0，提交修订 b11-e2-r1 记录校验收紧 | CHANGELOG、Schema、跨字段校验 |

## 不等同于已经执行的事项

- 镜像基线已在孙静怡机器构建并留证，约 406 MB；没有发布 registry 或导出归档。后续采用 docker save/load 交付时需带归档 SHA-256，实际接收再记录，不把本地 tag 当作可拉取地址。
- 环境哈希计算规范由胡博/A11 在 E3 实际增量检测前落实，DRAFT 负责给出平台、工具版本和配置；当前 E2 只固定字段与同环境语义，不填造假的运行哈希。已有样例值是格式展示。
- 三轮交接内容已通过文档和样例覆盖。没有 A11 端执行日志，因此不声称已完成跨机器读取、真实检测器重检或四服务联调。
- 本轮修复的 MDFixer 是本地原型，需显式 --local，不使用 input.image 启动容器；自动 DRAFT 与服务部署按 E3 推进。
