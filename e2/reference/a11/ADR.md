# 架构决策记录（ADR）

> 每条包含：背景（Context）→ 决策（Decision）→ 备选方案（Alternatives）→ 后果（Consequences）。
> 决策尽量给出**可验证的理由**，而不是"因为课程这么要求"。

---

## ADR-001 异步 Job

**背景**：构建与检测的耗时远超 HTTP 请求生命周期。这不是推测 —— 四篇论文原文可核的实测数据如下：

| 来源 | 论文原文表述 | 出处（`papers-text/` 行号） |
| --- | --- | --- |
| ISSTA'24 EChecker | OpenCV 的 **clean build 在本机超过 1 小时**（"OpenCV clean builds on our machine in over an hour"） | `_ISSTA_2024` L133–134 |
| TSE BuildChecker | Mkcheck 在大型项目上的检测耗时**可达数小时甚至数天**（"can be as long as hours or even days"） | `_TSE` L340 |
| ASE'25 MDfixer | 修复单项目**最长 788.313 秒**（unbound）；平均 198.386 秒，中位 62.999 秒 | `_ASE_2025` L1148 / L1151 |
| ICSE'26 DRAFT | 生成 Dockerfile **最长 19.57 分钟**（"19.57 minutes at maximum"） | `_ICSE_2026` L66 / L215 |

> 全部数字均可在提取文本中按行号复核。**本组曾在此处写错三个数字**（把论文中「OpenCV 检测只要约 1 小时」的举例误记成 77 小时，另两个属臆造），修正记录见 `CHANGELOG.md` 与 `AI_USAGE.md`。

**决策**：创建端点 `POST /v1/*-jobs` 受理后立即返回 **202 + job_id**；消费者用 `GET /v1/jobs/{job_id}` 轮询状态并取产物引用。

**备选方案**：同步等待。实现更简单，但客户端与执行过程强耦合：连接会超时、无法查询进度、无法取消。

**后果**：需要任务状态存储与查询接口；客户端需实现轮询。收益是受理与执行解耦、状态可观测（QUEUED → RUNNING → 终态）。

---

## ADR-002 产物访问：只传引用，URI 形式与访问方式解耦

**背景**：依赖图与日志体积可达 MB 级（实测单项目依赖图序列化后 40 KB ～ 1 MB）。若内联进响应体，每次轮询都要重复传输大文件，也无法单独下载与校验。PPT Slide 11 把"产物怎样存储和下载"列为必须自行决定的事项。

**决策**：
1. Job 只保存 **Artifact 元数据**（`artifact_id` / `type` / `uri` / `media_type` / `producer_job_id` / `commit` / `configuration_id` / 可选 `sha256`）；
2. URI 统一为 `artifact://<group>/<job_id>/<name>`，`<group>` 段让消费者一眼看出该找谁要文件；
3. **E2 阶段**用共享目录映射读取（`$ARTIFACT_ROOT/<group>/<job_id>/<name>`）；**E3 如需网络访问**再增加 `GET /v1/artifacts/{group}/{job_id}/{name}`，**URI 形式完全不变**。

**备选方案**：① 响应内联 base64 —— 响应体膨胀、无法流式下载；② 只提供 HTTP 端点 —— E2 阶段就得部署服务，与"不要求部署 API"的边界冲突；③ 直接把文件系统路径写进契约 —— 改为网络访问时会产生破坏性变更。

**后果**：E2 用最小成本即可满足"另一组能读取文件"的验证要求；从共享目录升级到网络端点**不需要改动任何契约字段**，避免 E3 返工。单点风险是共享目录必须双方可达且只读，已列入与 B11 的待确认项。

**读取步骤**（供 B11 参考）：从查询响应的 `output.artifacts[]` 找到目标 `type` → 取 `uri` → 按映射规则定位文件 → 若有 `sha256` 则校验完整性 → 需要追溯时用 `producer_job_id` 回查生产任务。

---

## ADR-003 版本兼容：`schema_version` 由请求方声明

**背景**：字段与语义变化可能破坏另一组的解析。PPT Slide 26 要求区分"可兼容变化"与"可能破坏兼容的变化"。

**决策**：
1. 用 `schema_version` 标识接口版本，当前为 `1.1.0`；
2. **创建受理响应（202）不含** `schema_version`，只回 `job_id` + `status`（与 PPT Slide 7 的响应样例 `{"job_id":…, "status":"QUEUED"}` 一致）；**查询响应（200）必须含** `schema_version` —— 它是完整 Job，消费者要据此判断这份结果按哪一版语义解释。两者用途不同，规则因此不同；
3. 新增**可选**字段 = 兼容；新增**必填**字段、删除/改名/改语义、修改状态枚举 = **不兼容**，须提升版本并同步更新 Schema、样例与 `CHANGELOG.md`；
4. 遇到不认识的主版本必须**拒绝**，不得按旧规则猜测解析。

**备选方案**：所有响应统一带版本（与 PPT 的 202 样例不符）；或所有响应都不带（查询响应无法自证版本）。

**后果**：
- 已知妥协：若未来需要多版本并存（同一服务同时服务 1.0 与 2.0 客户端），需重新评估本决策。已登记在 `STATUS.md`。
- **报文形态边界**（此前未定义，评审指出后补充）：本契约里有四种形态，用途不同，不可混为一谈：

| 形态 | 方向 | 含 `schema_version` | 满足完整 `Job` |
| --- | --- | --- | --- |
| 创建请求 | 客户端 → 服务端 | **必须** | 否（`CreateJobRequest`） |
| 受理响应 202 | 服务端 → 客户端 | 否 | 否（`DraftResponse`：`job_id` + `status`） |
| 查询响应 200 | 服务端 → 客户端 | **必须** | **是**（完整 `Job`，含 `input` 回显与 `output`） |
| 系统错误条目 `errors[]` | 服务端 → 客户端 | 否 | **否** —— 它是「任务以失败终态结束时的对外视图」，含 `job_id`/`job_type`/`status`/`error` 与可选 `execution`、`artifacts`；**不含** `input` 回显，**不含** `output.findings`（失败任务没有分析结论） |

---

## ADR-004 冗余依赖（RD）的处理与交接

**背景**：BuildChecker 与 EChecker 都能检测 RD（声明了但本配置未使用）。而 MDFixer 主要面向**缺失**依赖（MD）的修复。二者的处置风险不对等。

**决策**：
1. 接口中**完整定义** RD 数据结构（`type: "REDUNDANT"`，`evidence.actual_read=false` 且 `declared=true`）；
2. **E2 阶段 A 组仅报告 RD，不要求 MDFixer 自动修复**；B 组需能正确解析该结构，可选择忽略或仅展示；
3. `REPAIR` 任务的输入 `md_report_uri` **只消费 MISSING**。

**备选方案**：让 MDFixer 一并自动删除冗余声明。

**后果**（为什么不这么做）：冗余依赖在很多项目里是**跨配置的有意声明** —— 在另一个构建配置下它可能是必需的，自动删除会破坏那个配置的构建正确性。MD 的误添加风险低，RD 的误删除风险高，两者不应同策。RD 的处置建议仅作为报告输出，由人工决定。

---

## ADR-005 「检测发现」与「系统执行错误」必须分离

**背景**：这是最容易被设计错的一点。"检出缺失依赖"是**工具正常跑完并完成了它该做的事**；"工具没跑完"才是失败。若把检出 MD 当成错误状态，下游会误判（例如修复服务以为"检测失败了，别修了"），并污染监控告警。

**决策**：两条通路彻底分开，且**不允许在同一响应中共存**：

| 情形 | status | 载荷 |
| --- | --- | --- |
| 检出 MD/RD（可为 0 条） | `SUCCEEDED` | `output.findings[]` + `output.summary` |
| 工具自身没跑完 | `FAILED` / `TIMED_OUT` | `job.error{code, message, detail}` |

错误码按层分段，并明确与 HTTP 状态码的映射（此前只定义了 code 却没定义映射层，评审指出后补充）：

| code | HTTP | 层级 | 含义 |
| --- | --- | --- | --- |
| `VALIDATION_4001` | **400** | 入参契约层 | **请求方**提交的报文不符合契约（缺必填字段、枚举外取值、基线配置不一致等）。本组补充，用于课堂验收检查 02/03 |
| `CONTRACT_4002` | **400** | 协议层 | **任一方**产出的报文不符合已协商契约 —— 含生产方响应违约（如在全量检测响应里塞 `delta`）。消费者应**拒绝**该报文，不得静默忽略 |
| `ENV_3002` | **200** | 环境/镜像层 | 镜像构建失败等。任务已被受理，失败体现在 `status=FAILED` + `error` |
| `EXEC_4002` | **200** | 执行/调度层 | 超时等，体现在 `status=TIMED_OUT` |
| `ANALYSIS_5001` | **200** | 分析逻辑层 | 分析器自身失败，体现在 `status=FAILED` |
| `INTERNAL_5000` | **500** | 服务端未分类崩溃 | 真正的 HTTP 层内部错误，与「任务失败」不是一回事 |

> **关键区分**：`ENV_` / `EXEC_` / `ANALYSIS_` 三类是**任务失败**（HTTP 仍是 200）；只有 `INTERNAL_5000` 才是 HTTP 层错误。此前把「生产方报文违约」写成 `INTERNAL_5000` + 500，会与真正的服务端崩溃混为一谈 —— 已改为 `CONTRACT_4002` + 400。

**备选方案**：用同一个字段同时表达"发现了问题"与"执行出错"。

**后果**：`findings` 允许为空数组 ——「本次没发现问题」同样是成功。校验器强制断言二者不可共存。**课堂验收检查 04 的标准答案即此条**。

---

## ADR-006 `delta` 与 `findings` 必须正交，禁止用 delta 复述 findings

**背景**：增量检测天然有两个视角 —— 「哪里错了」（对错视角，`findings`）与「这次改动了哪些依赖关系」（结构视角，`delta`）。只看前者会丢掉一类关键信息：**变了但没错**。例如本次提交新增了 `#include "match.h"` 且在 Makefile 里**也正确声明了** —— 它不是缺失依赖，不会出现在 `findings` 里，但确实是依赖结构的真实变化。CI 靠它判断重编译范围，MDFixer 靠它理解"本次改动引入了什么"。

**决策**：
1. `delta` = 实际依赖图相对 `baseline_commit` 的**边级结构变化**（`added` / `removed`），每项含 `target` / `dependency` / **`declared`** / `commit`；
2. `declared=false` 的变化会同时出现在 `findings`（`origin=NEW`）；**`declared=true` 的变化是合法变化，只出现在 `delta`**；
3. `findings` 只记录错误状态；`delta` 记录全部变化，**不含对错判断**；
4. 两者**允许且应当不同**；禁止把 `findings` 的条目原样复制进 `delta`；
5. `delta` 仅对 `INCREMENTAL_CHECK` 有意义，出现在其他类型响应中即校验失败。

**备选方案**：① 不加 delta，让消费者下载两张图自己求差 —— 把计算与一致性问题推给下游；② delta 里放完整 `Finding`（含 `type: MISSING/REDUNDANT`）—— 这会诱导"只放有问题的变化"，使 delta 退化为 findings 的子集，**信息量为零**，且两处不同步时响应自相矛盾。

**后果**：本例样张中 `delta.added` 特意包含一条 `declared=true` 的合法变化（`src/match.o → src/match.h`）作为证据。**已知局限**：delta 是否已退化为复述属语义问题，结构校验无法自动判定，靠评审与本文约束。

---

## ADR-007 增量检测的基线必须绑定提交与构建配置

**背景**：增量检测的本质是"相对基线图求变化"，而**依赖图与构建配置强绑定**：同一份代码在不同构建配置下（条件编译、开关选项）实际依赖集合不同。配置不同的两张图求差会产生大量假差异 —— 而且**看不出来**，属静默错误。这一判断有论文依据：EChecker 明确承认其检测只能覆盖当前构建配置。

**决策**：`baseline` 必须包含 `commit`、`configuration_id`、`actual_graph_uri` 三要素，并额外要求 `build_environment_hash`；任一不满足即**拒绝**：

1. `baseline.commit` 必须等于 `input.base_commit`；
2. `baseline.configuration_id` 必须等于 `input.configuration_id`；
3. 缺 `baseline` 或 `build_environment_hash` 一律拒绝。

**备选方案**：只传 `actual_graph_uri`（更简洁）；或缺基线时自动降级为全量检测。

**后果**：调用方必须先拿到该 (commit, configuration_id) 的 FULL_CHECK 产物，存在前置依赖链路。**即使未来支持降级，也必须显式声明（如新增字段），不能静默降级** —— 静默降级会掩盖正确性问题。跨字段一致性无法由 JSON Schema 表达，由 `validate.py` 的业务规则兜住（检查 06）。

---

## ADR-008 失败处理规则：终态不可回退，候选被拒 ≠ 任务失败

**背景**：PPT Slide 11 要求决定"失败怎样处理"。任务可能在三类层面失败；此外 REPAIR 天然会出现"候选补丁被验证否决"的情况。

**决策**：
1. 错误码按层分段（见 ADR-005）；
2. **终态不可回退**：`SUCCEEDED / FAILED / TIMED_OUT / CANCELLED` 一旦写入不再变更；**重试必须提交新任务**，不复用原 `job_id`；
3. `CANCELLED` 仅在 `QUEUED` / `RUNNING` 阶段被接受；
4. **候选被拒不是任务失败**：REPAIR 返回 `candidates_rejected > 0` 时 `status` 仍为 `SUCCEEDED`。

**备选方案**：允许 `FAILED` 任务原地重试。

**后果**：客户端用新任务表达重试，代价是多一条记录；收益是任何一份响应在任意时刻都有**唯一确定的含义**（这是可追溯性的前提）—— 否则同一个 `job_id` 会在先后两个时刻对应两次不同执行，`execution` 时间字段也会自相矛盾。

---

## ADR-009 `job_id` 由服务端生成，客户端用 `idempotency_key` 表达同一请求

**背景**：Job 是异步的。若由客户端指定 `job_id`，会出现编号冲突、被猜测，以及"同一逻辑请求重复执行"的问题。

**决策**：`job_id` 由服务端生成；客户端在**顶层** `idempotency_key` 中表达"这是同一个逻辑请求"—— 相同幂等键重复提交返回既有 `job_id`，不重复执行。

**备选方案**：客户端指定 `job_id` —— 直观，但冲突与重放风险不可控。

**后果**：幂等键需包含足够信息量，本组样例采用可读拼接 `组号|项目|commit|base|config`，便于排查；服务端需维护"幂等键 → job_id"映射。
