# A11-B11 E2 接口契约

| 项 | 内容 |
| --- | --- |
| A 组 | **A11**（BuildChecker、EChecker） |
| B 组 | **B11**（DRAFT、MDFixer） |
| 协商时间 | 2026-09-19（E2 课堂） |
| 仓库地址 | https://git.nju.edu.cn/devops-group11/devops-group11.git |
| 接口版本 | **1.1.0** |

## 服务交接

```
DRAFT (B11) ──环境、镜像、日志──▶ BuildChecker (A11)
                                       │
                              全量图、MD/RD 报告
                                       ▼
                                  EChecker (A11)
                                       │
                          增量图、错误变化、delta
                                       ▼
                                  MDFixer (B11)
                                       │
                              Patch、修复报告、日志
                                       ▼
                              重新验证（构建、测试、重检）
                                       │
                              决定是否接受补丁
```

### RD（冗余依赖）数据流向 — 重要

- BuildChecker 与 EChecker **都会输出 RD**（`findings` 中 `type: "REDUNDANT"`），与 MD 并列在同一个报告里；
- 但按 **ADR-004**，**MDFixer 在 E2 阶段不执行 RD 的自动修复**，只需能**正确解析**该数据结构（可选择忽略或仅展示）；
- `REPAIR` 的输入 `md_report_uri` **只消费 MISSING**；
- 理由：冗余声明可能是**跨配置的有意声明**，误删会破坏其他配置的构建正确性；MD 误添加风险低，RD 误删除风险高。

### 增量检测链（A 组内部）

```
FULL_CHECK(C0) ──产出 ACTUAL_GRAPH──▶ 作为 INCREMENTAL_CHECK 的 baseline
                                             │
                                     产出更新后的图 current_graph_uri
                                             │
                                    ▼ 供 C1 → C2 继续链式检测
```

## 文件索引

| 文件 | 内容 |
| --- | --- |
| **`说明.md`** | **文件导读**：每个文件是干什么的、谁看、什么时候用；含三个"活"文件与交付前检查清单 |
| `task.schema.json` | 公共 Job 与四类输入输出定义（含 `delta`、`build_environment_hash`、`suggested_fix`、`current_graph_uri`） |
| `contract-examples.json` | 四类请求、202 受理响应、四类查询响应、系统错误、MD/RD 发现、产物元数据、6 类非法输入 |
| `validate.py` | 契约与样例校验脚本。**必填规则与全部枚举在运行时从 `task.schema.json` 派生，脚本内不重复定义**（避免契约与校验器各写一套、靠人工同步） |
| `openapi.yaml` | 接口说明（可选文件）：四个创建端点 + 查询端点 + 产物下载端点 |
| `ADR.md` | 9 条架构决策：异步 Job、产物访问、版本兼容、RD 处理、发现与错误分离、delta 正交、基线一致性、失败处理、job_id 生成 |
| `Backlog.md` | 任务、负责人、产物、验收条件、状态 |
| `AI_USAGE.md` | AI 使用记录：工具、提示摘要、建议、人工采纳或拒绝理由、验证方式 |
| `CHANGELOG.md` | 接口版本与兼容性判断 |
| `CONTRIBUTIONS.md` | 成员、文件、仓库地址与分支、Issue/PR、协商结论（**暂不含提交 SHA** —— 仓库尚未推送成功，无可核对的 SHA） |
| `STATUS.md` | 已完成项与验证结果、未完成项、已知局限 |

## 校验

```bash
python validate.py
```

预期输出：**42 项全部通过，退出码 0**。输出分三部分：

| 部分 | 内容 | 项数 | 依赖 |
| --- | --- | --- | --- |
| 第一部分 | 契约检查（四类请求 / 五类响应 / 三种系统错误 / 六类非法样例） | 18 | 无 |
| 第二部分 | **负向对照** —— 篡改完整合法样例且只改一处，期望被拒绝 | 15 | 无 |
| 第三部分 | `jsonschema` 标准 Schema 交叉校验 | 9 | 需 `jsonschema` 库；未安装则跳过，不影响结论 |

> **第二部分是这份交付物的关键**：正向校验只能证明"合法的能通过"，证明不了"非法的会被拒"。
> 三部分内容都在包内，任何人都能当场复算 —— 不存在"文档声称了某个数字，但包里找不到执行它的东西"的情况。

覆盖范围对应课堂验收（PPT Slide 25）：

| # | 检查 | 本仓如何满足 |
| --- | --- | --- |
| 01 | 运行 `validate.py`，检查四类请求与响应 | 42 项全部通过（零依赖 33 + jsonschema 9） |
| 02 | `job_type` 改成 `ABC`，应被拒绝 | `invalid.unknown_job_type` → `VALIDATION_4001` |
| 03 | 删除增量任务的 `baseline`，应被拒绝 | `invalid.missing_baseline` → `VALIDATION_4001` |
| 04 | 解释 MD 为什么不等于工具执行失败 | ADR-005 + 校验器输出的检查 04 说明 |
| 05（本组自加） | `findings` 与 `delta` 必须正交 | ADR-006 + 校验器检查 05 |
| 06（本组自加） | 基线提交与配置必须一致 | ADR-007 + 校验器检查 06（跨字段校验） |

## 接口一览

| 操作 | 端点 | 所属 | 样例位置 |
| --- | --- | --- | --- |
| 全量检测 | `POST /v1/full-check-jobs` | **A11** | `contract-examples.json` → `requests.FULL_CHECK` |
| 增量检测 | `POST /v1/incremental-check-jobs` | **A11** | `requests.INCREMENTAL_CHECK` |
| 生成构建环境 | `POST /v1/dockerfile-jobs` | B11 | `requests.DRAFT` |
| 修复缺失依赖 | `POST /v1/repair-jobs` | B11 | `requests.REPAIR` |
| 查询任务 | `GET /v1/jobs/{job_id}` | A11/B11 共同 | `responses.query_*` |
| 产物下载（E3 备用） | `GET /v1/artifacts/{group}/{job_id}/{name}` | A11/B11 共同 | ADR-002 |

> 端点命名沿用 PPT Slide 27 的参考值，**属可协商项**，以与 B11 的最终协商为准。

## 产物访问约定（`artifact://` 如何解析）

对应 PPT Slide 11「产物怎样存储和下载」与 Slide 24「约定解析器或实际下载接口」。

**URI 形式**：`artifact://<group>/<job_id>/<name>`

| 段 | 含义 | 示例 |
| --- | --- | --- |
| `<group>` | 生产方组号 | `a11`、`b11` |
| `<job_id>` | 生产该产物的任务编号 | `job-full01` |
| `<name>` | 文件名 | `actual.json`、`fix.patch` |

**E2 阶段（方案 A · 共享目录映射）**

```
artifact://a11/job-full01/actual.json
        ↓ 映射
$ARTIFACT_ROOT/a11/job-full01/actual.json
```

**E3 如需网络访问（方案 B · 下载端点）**：`GET /v1/artifacts/{group}/{job_id}/{name}` → `200` 文件字节流 / `404` 产物不存在。

> 两个方案的 **URI 形式完全一致**，因此从 A 切到 B **不需要修改任何契约字段** —— 这是刻意设计，避免 E3 返工。

**消费方读取步骤**（以 B11 读取 A11 的依赖图为例）：

1. 从查询响应的 `output.artifacts[]` 找到 `type = "ACTUAL_GRAPH"` 的条目；
2. 取其 `uri`，例如 `artifact://a11/job-full01/actual.json`；
3. 按 §映射规则定位文件并读取；
4. 若该条目带 `sha256`，读取后校验完整性 —— 不匹配即视为产物损坏，拒绝使用；
5. 需要追溯时用 `producer_job_id` 回查生产任务。

| 约定项 | 内容 |
| --- | --- |
| 完整性 | `sha256` 可选；关键产物（依赖图、补丁）建议携带 |
| 媒体类型 | `media_type` 必填，消费者**不得**靠扩展名猜类型 |
| 生命周期 | E2/E3 期间长期保留、不自动清理；清理须双方确认 |
| 命名冲突 | 同一 `job_id` 下 `name` 唯一；不同任务天然隔离在不同目录 |

**各产物与服务的对应关系**

| 产物 | 生产者 | 消费者 | 用途 |
| --- | --- | --- | --- |
| `ACTUAL_GRAPH` | BuildChecker (A11) | EChecker (A11)、B11 | 实际依赖图 / 增量检测的基线 |
| `DECLARED_GRAPH` | BuildChecker (A11) | B11 | 与声明对照 |
| `ERROR_REPORT` | BuildChecker / EChecker (A11) | MDFixer (B11) | 修复输入（仅消费 MISSING） |
| `TRACE_EVIDENCE` | BuildChecker (A11) | A11、B11 | 进程与文件级证据 |
| `PATCH` / `STYLE_REPORT` | MDFixer (B11) | A11（重检） | 修复产物与声明风格说明 |
| `DOCKERFILE` / `IMAGE` | DRAFT (B11) | A11（提供检测环境） | 可构建环境 |

## 设计原则

1. **字段名最大化沿用课程给定词汇** —— PPT 出现过的字段一律不改名（如产物类型用 `ERROR_REPORT`，对应 PPT Slide 9）。
2. **能拒绝就不猜** —— 缺 `baseline`、缺环境哈希、基线提交或配置不匹配、`job_type` 未知、主版本不支持、`delta` 用错位置，一律拒绝而非静默降级。
3. **三重正交** ——「检出问题」与「工具失败」（ADR-005）、「哪里错了」与「哪里变了」（ADR-006）、「请求体」与「响应体」（ADR-003）都不得混在一个字段里。
4. **大文件走引用，且 URI 与访问方式解耦** —— E2 共享目录、E3 可换域名端点而不改契约（ADR-002）。
