# CHANGELOG

记录接口版本、字段变更、语义变化、受影响样例、Schema 修改与兼容性判断。

| 版本 | 日期 | 变更 | 影响 | 兼容性 | 关联文件 |
| --- | --- | --- | --- | --- | --- |
| 1.0.0 | 2026-09-19 | 首次定义公共 Job 与四类任务输入输出（DRAFT / FULL_CHECK / INCREMENTAL_CHECK / REPAIR）；定义状态枚举、系统错误、Finding、Artifact 与 `artifact://` 引用 | A11、B11 | 初始版本。**从未对外发布** —— 与 1.1.0 同日产生，1.1.0 才是首个对外版本（因此本文件不构成"破坏性变更却只升次版本"的问题） | `task.schema.json`、`contract-examples.json` |
| 1.1.0 | 2026-09-19 | ① `IncrementalCheckOutput` 增加 `delta`（`baseline_commit` + `added`/`removed`，每项带 `declared`）；② `Finding` 增加 `suggested_fix`；③ `IncrementalCheckInput` 增加必填 `build_environment_hash`；④ `Output` 增加 `current_graph_uri`；⑤ `Artifact` 增加 `commit`/`configuration_id`；⑥ 补充 REDUNDANT 样例与 6 类非法输入样例；⑦ `IncrementalCheckInput.configuration_id` 由可选改为**必填**（见下方修正记录） | A11、B11 | **部分不兼容**：③⑦ 为新增**必填**字段，旧版 INCREMENTAL_CHECK 请求将被拒绝；其余为新增字段，向后兼容 | `task.schema.json`、`contract-examples.json`、`validate.py`、`ADR.md`、`Backlog.md`、`STATUS.md` |

## 修正记录

| 日期 | 问题 | 根因 | 修正 |
| --- | --- | --- | --- |
| 2026-09-19 | `baseline.configuration_id` 与本次不一致时**未被拒绝**（契约承诺了规则，实际执行不了） | `IncrementalCheckInput` 顶层没有必填的 `configuration_id`，校验规则**缺少对照物** → 条件恒不成立、**静默失效**。属契约结构缺陷，不是校验代码笔误 | 将 `configuration_id` 改为必填（`task.schema.json` + `validate.py` + `contract-examples.json` 三处同步），规则改为"基线配置缺失即拒绝、与本次不一致即拒绝" |

> **该问题由「负向对照校验」发现，而非正向校验。** 正向校验只能证明"合法的能通过"，证明不了"非法的会被拒" —— 后者才需要刻意设计对照实验：篡改合法样例，期望被拒绝。

### 第二轮：外部评审指出的 15 项问题

| 日期 | 问题 | 根因 | 修正 |
| --- | --- | --- | --- |
| 2026-09-19 | ① 文档声称「负向对照 13 项」，但包内**没有任何东西能复算它**（原先是临时脚本，跑完即删）；② 契约的必填规则在 `validate.py` 里**硬编码了第二份**；③ 反例隔离度不足 —— `missing_baseline` 一次缺 6 个字段，回答不了"只缺 baseline 会拒绝吗"（正是课堂检查 03 的原题）；④ 三处引用了**一个**不存在的 ADR 编号**（当时误写）**；⑤ `validate.py` 的 URI 校验只做 `startswith`，**比它声称遵守的 schema 更松**；⑥ ADR-003 说"响应体不重复声明版本"，但四个查询响应都带了；⑦ 不兼容变更却只升次版本；⑧ ADR-001 的四个引用数字有三个核不上 | 均为**过程性问题**：验证靠一次性脚本；契约与校验器双份定义；反例构造未做"只改一处"隔离；重排 ADR 编号后漏改引用；校验逻辑与 schema 各写一套 | ① 15 项负向对照**做进 `validate.py` 第二部分**，随包可复算；② 校验器的枚举与必填规则**改为全部从 schema 派生**（单一来源）；③ 反例全部重构为「完整合法请求 + 只改一处」；④ 修正为 `ADR-006`；⑤ URI 两级收紧为三段式；⑥⑦⑧ 见 `ADR.md` ADR-003、本文件版本表、ADR-001 数据表 |

## 兼容性约定（对照 PPT Slide 26）

| 变更类型 | 判定 | 处理 |
| --- | --- | --- |
| 新增**可选**字段 | 兼容 | 需消费者允许（不得开启严格拒绝未知字段的模式），同步更新共享 Schema |
| 新增**必填**字段 | **不兼容** | 已对外发布的版本之间须提升**主版本**；若双方均未对外发布（本组 1.0.0 → 1.1.0 即属此情形），可用次版本，并在本文件写明"未发布" |
| 删除字段、改名、改变字段语义 | **不兼容** | 提升主版本 |
| 修改状态枚举 | **不兼容** | 提升主版本 |
| 单纯补充样例、修文档 | 兼容 | 不需提升版本 |

## 待记录

E3 阶段若出现新的字段变更，在本表追加一行，并同步更新 `task.schema.json`、`contract-examples.json` 与 `STATUS.md`。
