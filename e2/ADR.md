# B11 E2 架构决策

2026-09-22 提交版；确认依据见 AGREEMENT。A11 的原始九条 ADR 在 reference/a11/ 保留为历史来源。

## ADR-001 异步 Job 与结果语义

Context：四服务执行耗时不同，需要统一受理和查询。Decision：沿用四种 job_type、六态，POST 202 返回 job_id/job_type/QUEUED，GET 返回完整 Job。SUCCEEDED 可以报告 MD/RD；FAILED/TIMED_OUT 返回空 output 和 error。Alternatives：同步等待实现简单但耦合客户端超时。Consequences：E3 实现任务存储；E2 用正式 Schema 与样例验证。

## ADR-002 产物按 URI 和目录映射交接

Context：图、日志、补丁不适合塞进每次响应。Decision：artifact URI 映射 ARTIFACT_ROOT，小文件用目录/ZIP 交换，元数据包含类型/生产者/媒体类型，有摘要必须校验。镜像后续通过 docker save/load 等方式取得，tag 不表示远端可用。Alternatives：HTTP 服务或共享机器；本阶段增加部署成本。Consequences：本地验证文件读取，实际 A11 读取和镜像交付另留执行证据。

## ADR-003 报告只消费有效 MD

Context：混合报告还包含 RD，增量发现可能已消除。Decision：MDFixer 只取 MISSING 且非 RESOLVED，源码/报告/Makefile commit 匹配，位置对应同一文件；RD 保留不删除。Alternatives：A11 单独导出 MD 报告。Consequences：消费方明确筛选；人工报告标 MANUAL，不借用真实检测器名称。

## ADR-004 接口修订与来源保留

Context：原校验遗漏内部输入和失败视图；直接覆盖会丢失证据。Decision：A11 快照保持字节不变，正式 Schema 放 e2 根目录，补缺字段及已有语义约束。协议保持 1.1.0，提交修订 b11-e2-r1；不宣称收紧校验对宽松旧样例兼容。Alternatives：原样接受无法抓出实际缺陷。Consequences：校验、样例、OpenAPI、变更和来源记录同步，消费者以提交版为准。

## ADR-005 本地 MDFixer 的可信验证

Context：成员原型存在上传转义错误、无源码示例和未执行重检计数。Decision：修复原型，显式 --local，固定工作区 HEAD，临时应用候选后恢复原 Makefile；输出补丁供独立应用。构建/测试命令限时，重检未运行则 NOT_RUN。Alternatives：把一切实现为容器服务超出 E2；仅检查 JSON 无法验证补丁。Consequences：包含可运行教学源码 bundle；支持简单显式规则，复杂规则拒绝，不声称完整论文复现。

## ADR-006 幂等与重试

Context：创建重发可能重复执行。Decision：服务按 job_type + idempotency_key 定位逻辑请求，同键同输入复用原任务，同键异输入返回 HTTP 409 / CONTRACT_4002；新执行新键新 job_id，同一流程可复用 trace_id。Alternatives：仅定义拼接字符串不足以明确行为。Consequences：E2 记录协议；CLI 单次执行不实现持久化幂等，E3 加服务存储。

## ADR-007 配置与环境

Context：基线只能在可比配置下使用。Decision：接受 fzy 的 Ubuntu24.04/GCC13/Make4.3 基线，configuration_id 固定记录；incremental baseline 的 commit/config 与请求匹配。环境哈希具体规范在 E3 与 A11 落实，DRAFT 给出工具版本等材料，不把源码 C0/C1 变化简单混入同环境判定。Consequences：E2 表达字段和拒绝条件；未完成真实增量运行不填造假的实际哈希。
