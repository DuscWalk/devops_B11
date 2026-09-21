# B11 公共契约审阅

审阅人/任务负责人：胡博（Codex 辅助准备）；日期：2026-09-21。基线为 [A11 来源快照](reference/README.md)。已收到孙静怡 feat/draft 的回复，见 [审阅记录](feedback/draft-2026-09-21.md)；公共技术方案仍待 A11 确认，未记录尚未发生的双方协商。

## 审阅结论

原始校验器在 Python 3.10.12、jsonschema 4.25.1 下为 **42/42 通过**。补充按任务类型选择输入 Schema 后，原样例为 **7/8 通过**，增量查询回显缺少 `configuration_id`。因此“原校验通过”尚不能作为接受全部接口的依据。

只补该字段的 [建议样例](proposals/README.md) 已通过 8/8 输入检查。原始快照与原始失败证据均保留。A11 快照的产物引用仍只有元数据样例。孙静怡另提供 5 份可读 DRAFT 文件样例和真实本地镜像执行记录；尚未完成向 A11 交付镜像，依赖图、固定 MD 报告与补丁也待交接。

## Q01 公共模型、端点和样例遗漏

需要确认：胡博、A11；两位服务负责人确认各自端点。

建议沿用现有四个任务类型和端点：DRAFT → `POST /v1/dockerfile-jobs`，FULL_CHECK → `POST /v1/full-check-jobs`，INCREMENTAL_CHECK → `POST /v1/incremental-check-jobs`，REPAIR → `POST /v1/repair-jobs`；查询用 `GET /v1/jobs/{job_id}`。

公共字段沿用 `schema_version`、`trace_id`、`job_type`、`idempotency_key`、`input`；`job_id` 由服务端生成。状态沿用 QUEUED / RUNNING / SUCCEEDED / FAILED / TIMED_OUT / CANCELLED。检测发现 MD/RD 属于成功分析的 findings，系统执行异常属于 error。

需要 A11 接受的具体修正：`responses.query_incremental_check.input` 增加 `configuration_id: cc-MODE0`。现有请求已有该值，Schema 也要求该字段。建议上游校验器同时校验请求和查询回显的服务输入定义。B11 已准备修正样例和验证，未修改原始 Schema。

证据：[原件扩展检查](evidence/reference-validation-2026-09-21.txt)、[建议样例检查](evidence/proposal-validation-2026-09-21.txt)。

## Q02 产物实际访问和摘要

需要确认：胡博、A11；孙静怡/王硕说明各自产物。

建议沿用 `artifact://<group>/<job_id>/<name>` 映射到 `$ARTIFACT_ROOT/<group>/<job_id>/<name>`。E2 可先交换小型固定样本目录，每台机器用自己的根目录读取；若选共享机器，应给出双方实际可达的路径与权限。仅创建同名本地目录不构成共享。

待回复：采用目录/压缩包交换还是共享主机；具体位置；由谁提供第一份文件；哪些产物强制摘要；保留多久；读取失败如何处理。A11 README 写 sha256 可选，Backlog 建议图和补丁强制，需统一。建议关键产物含真实摘要，日志可选；出现摘要不匹配时拒绝消费。

本地已验证 [产物读取演示](artifact-access.md)。它是 B11 编写的文本演示文件，不是 A11 产物、依赖图或执行日志。

## Q03 DRAFT 环境交接

需要确认：孙静怡、A11，胡博汇总。

孙静怡已回复：沿用 DRAFT 端点与必填字段，固定 fzy `28195b3a709995354b6c33cec9bb7c9f81532eb6`，工作目录为仓库根，构建用 `make clean && make`，验证用 `make check && ./fzy --help`；5 次迭代/1800 秒作为建议默认值。具体回复与验证见 [反馈审阅](feedback/draft-2026-09-21.md)。

新分支已有 IMAGE 文件、每轮日志/理由、TEST_RESULT 和真实摘要，胡博现有读取器可读取全部 5 个演示文件。格式仍为提议。实际镜像只在孙静怡本机 Docker daemon；需 A11 确认 registry 或 docker save/load 交付，并规范最终 IMAGE 文件。真实执行证据里的 configuration_id_proposal / repo_digests 与契约示例字段不同，不应直接充当最终交接 JSON。

构建配置与环境标识如何从 DRAFT 交给检测服务，见 Q07。当前示例中的成功数值没有被本组当作真实构建证据。

## Q04 MDFixer 报告消费

需要确认：王硕、A11，胡博汇总。

请王硕检查 `requests.REPAIR` 和 `responses.query_repair`，确认报告文件的完整 JSON 外壳、Makefile 的定位方式、构建/验证命令、补丁及风格报告内容、候选拒绝原因和重检结果。

A11 查询响应的 findings 同时含 MISSING 与 REDUNDANT，Backlog 又建议修复 URI 指向“仅含 MISSING”的报告。待决定：A11 生成专用 MD 报告，还是 MDFixer 读取混合报告并筛选。

供讨论的建议：保留检测混合报告，由消费方只选当前版本仍有效的 MISSING；忽略 REDUNDANT，增量结果中 `origin=RESOLVED` 的发现也不送去修复。报告 commit 与源码不符则拒绝。需王硕确认可实现，并与 A11 明确过滤发生在哪一侧。

包里的 fzy 路径、行号和发现属于契约样例。孙静怡发现实际 Makefile 位于根目录；胡博本次对固定提交获取原文件复核：Makefile 可读，src/Makefile 不存在。因此原 REPAIR.makefile_uri 及 findings.location.file 不能直接作为真实输入，需王硕和 A11 重新核对路径、行号与证据。王硕负责后续固定 MD 样本和来源标注，不能把当前样例直接登记为真实检测结果。

## Q05 创建响应、运行状态和失败响应

需要确认：胡博、A11、两位服务负责人。

现有说明称 202 响应只需 job_id + status，而 `DraftResponse.required` 还要求 job_type；该 Schema 的 status 允许全部六态，未限制为 QUEUED。建议正式约定 202 返回 job_id、job_type、status=QUEUED，并统一文档和 Schema。

现有 `errors[]` 被原校验器专门当作失败视图片段处理，缺少 schema_version、trace_id、execution、input、output，不能直接作为完整 Job 返回。OpenAPI 的 GET 又引用统一 Job。待决定：GET 始终返回完整 Job，还是为失败视图增加明确的联合类型。

建议采用完整 Job；排队/运行/失败时用空 output 对象表示暂无成功产物，失败时填写 error。状态与 output/error/时间字段的关系还需写进正式约束。候选修复被拒绝是否属于正常任务结果，也请王硕确认。

证据：[结构诊断](evidence/reference-audit-2026-09-21.json)。目前本地草案未替双方改这些协议规则。

## Q06 幂等、冲突和重试

需要确认：胡博、A11。

原草案给出键的拼写建议，但仍需明确同键重发、同键不同输入、终态后重试的行为。建议按 `(job_type, idempotency_key)` 区分命名空间，同键同输入返回原任务；同键不同输入明确报冲突，HTTP 状态和错误码由双方确定。新一次执行使用新键和新 job_id，同一平台流程继续携带 trace_id。请勿只确认字符串拼法而遗漏行为。

## Q07 配置、环境哈希与版本变更

需要确认：孙静怡、胡博、A11。

孙静怡提供 Ubuntu24.04/GCC13.3/Make4.3 实测候选，配置提议为 fzy-default-gcc13-make4.3；A11 原样例为 Ubuntu22.04/GCC10，须确认是否接受新环境。沿用完整源码 SHA 和 configuration_id，增量基线提交/配置应与请求对应。build_environment_hash 目前有字段和语义，尚未约定算法及基线侧的比较依据。建议 E2 明确由谁提供、怎样交接；具体算法可以作为有负责人的 E3 待办，正式运行前完成。

输入 Schema 多处 `additionalProperties: false`，新增可选字段也可能被旧消费者拒绝。建议字段变动同步 Schema、样例、校验器和变更记录，不在双方确认前宣布兼容或发布新共享版本。
