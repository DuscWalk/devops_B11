# AI_USAGE

记录工具或模型、设计任务、提示摘要、AI 建议、人工采纳或拒绝理由、修改文件、提交版本与验证方式。

| 日期 | 工具或模型 | 任务 | 提示摘要 | AI 建议 | 人工处理 | 关联文件 | 验证 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-09-19 | 对话式助手 | Job 状态设计 | 为耗时任务设计状态 | 建议使用 `PENDING` 表示排队 | **拒绝**：改为课程规定的 `QUEUED`，枚举统一为六态 | `task.schema.json`、`contract-examples.json` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | 异步 Job 决策 | 是否需要异步 | 建议异步 Job，并列出基线工具耗时数据作为理由 | **采纳，但论据被人工核实后大幅修正**：写入 ADR-001，耗时数据改为论文原文可按行号复核的表述（OpenCV clean build 超过 1 小时 / Mkcheck 大项目可达数小时甚至数天） | `ADR.md` | 人工复核论文原文通过 |
| 2026-09-19 | 对话式助手 | 产物过大的处理 | 依赖图能否直接放进响应 | 建议内联 JSON | **拒绝**：改为 `artifact://` 引用，理由是大文件会让轮询响应膨胀 | `ADR.md`（ADR-002）、`task.schema.json` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | Delta 结构设计 | 为增量输出增加变化量 | 建议增加 `delta.added` / `delta.removed` | **部分采纳并修正**：采纳字段，但把每项定义为 `{target, dependency, declared}` 而非完整 Finding，理由是后者会让 delta 退化为 findings 子集（见下行） | `task.schema.json`、`contract-examples.json`、`ADR.md`（ADR-006） | `python validate.py` 通过 |
| 2026-09-19 | **另一 AI 的审查意见** | Delta 定义复核 | 审查认为应补 `delta`，示例为把 `findings` 中 `origin=NEW` 的条目复制进 `delta.added` | 补齐 `delta` 字段 | **部分采纳 + 修正定义**：方向对（确实需要结构视角），但示例是错的 —— 那样 delta 只是 findings 的子集，信息量为零，还引入两处不同步就自相矛盾的风险。改为记录"依赖边变化"并加 `declared` 标志，使**合法变化**有处安放 | `ADR.md`（ADR-006）、`contract-examples.json` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | 环境哈希校验 | 防止跨环境基线数据导致误报 | 建议增加 `build_environment_hash` | **采纳**：设为 `IncrementalCheckInput` 必填，并在校验器中做存在性与一致性检查 | `task.schema.json`、`validate.py` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | RD 处理策略 | 冗余依赖是否交给 MDFixer 修复 | 建议一并在 MDFixer 中自动删除 | **拒绝**：RD 可能是跨配置的有意声明，误删会破坏其他配置。改为"仅报告、不自动修复"，写入 ADR-004 | `ADR.md`（ADR-004）、`Backlog.md` | 人工审查通过 |
| 2026-09-19 | 对话式助手 | 建议修复字段 | 为 Finding 增加修复建议 | 建议增加 `suggested_fix`（字符串） | **采纳**：设为可选字段，定位为"给 MDFixer 的线索"，具体补丁仍由 B 组按其声明风格策略生成 | `task.schema.json`、`contract-examples.json` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | 产物类型命名 | 报告类产物的类型名 | 建议用 `FINDING_REPORT` | **拒绝**：PPT Slide 9 原文为 `ERROR_REPORT`，沿用课程词汇避免与助教对照检查时产生歧义 | `task.schema.json`、`contract-examples.json` | 对照 PPT 复核通过 |
| 2026-09-19 | 对话式助手 | 错误码体系 | PPT 只给了三个系统错误码，请求非法如何表达 | 建议无（未覆盖） | **人工补充**：增加 `VALIDATION_4001`（入参契约层）与 `INTERNAL_5000`，使课堂验收检查 02/03 有明确的拒绝表达 | `task.schema.json`、`validate.py`、`contract-examples.json` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | 校验器实现方式 | 用什么实现校验 | 建议直接依赖 `jsonschema` 库 | **部分采纳**：以零依赖内置规则为主（助教需在任意机器直接运行），若环境存在 `jsonschema` 则**额外**执行一次标准 Schema 交叉校验 | `validate.py` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | 交叉校验发现的问题 | 用标准 Schema 复核样例 | 无（此为本组主动增加的检查） | **人工发现**：交叉校验抓出手写校验器放过的问题 —— 查询响应样例缺 `schema_version` 与 `input` 回显，与 `Job` schema 不一致；已修正并通过 | `contract-examples.json`、`validate.py` | `python validate.py` 通过 |
| 2026-09-19 | 对话式助手 | 验证方法设计 | 正向校验通过是否足够 | 无（此为本组主动增加的检查） | **人工补充「负向对照」**：篡改合法样例，期望被拒绝。**由此发现真 bug** —— `IncrementalCheckInput` 缺必填 `configuration_id`，导致"基线配置必须与本次一致"这条规则因**缺少对照物而静默失效**（契约承诺了规则却执行不了）。已修正 schema、校验器与样例三处 | `task.schema.json`、`validate.py`、`contract-examples.json`、`CHANGELOG.md` | 独立负向对照 **13 项 全部被拒绝**；正向样例、独立 `jsonschema` 复核与端到端校验全部通过 |
| 2026-09-19 | 对话式助手（本组） | ADR-001 论据核实 | 用本地论文提取文本逐个核查 ADR 中引用的四个耗时数字 | （此前凭记忆写出四个数字） | **人工核查发现三个错误并全部修正**：①「Mkcheck 检测 OpenCV 约 77 小时」—— 论文原文实为「OpenCV 检测只要约 1 小时」，那是**相对快**的举例，方向记反且数值臆造；②「OpenCV 全量构建约 2.4 小时」—— 原文为「clean build 超过 1 小时」；③「MDfixer 单项目最长 1,338 秒」—— 原文为 **788.313 秒**。仅「DRAFT 最长 19.57 分钟」准确 | `ADR.md`、`CHANGELOG.md` | 四个数字现均可在 `papers-text/` 按行号复核 |
| 2026-09-19 | **另一 AI 的评审意见** | 交付物外部复核 | 全文审查交付物，列出 A/B/C 三级问题 | 指出 15 项问题（A 级 5 项、B 级 9 项、C 级若干） | **逐条核实后采纳**：经复核属实并已修正的有 ——「13 项 无法复现」（我用了临时脚本，跑完即删，包内无物可复算）、「契约与校验器双份定义」、「反例隔离度不足」、「引用了不存在的 一个不存在的 ADR 编号」、「URI 校验比 schema 更松」、「ADR-003 与样例矛盾」、「版本口径自相矛盾」、「四个引用数字核不上」。属已决定处理方式的（`.git` 已移除、仓库不推送）仅同步文档表述 | 全部 13 个文件 | `python validate.py` → **42 项通过**（零依赖 33 + jsonschema 9） |

## 说明

1. 本表只记录**真实发生**的交互与判断，不美化；凡"采纳"均说明理由，凡"拒绝"均说明风险。
2. **提交版本**：**暂无**。本地 Git 仓库已移除、远端推送被拒（空仓库初始提交需 Maintainer 权限），因此当前**不存在可被第三方核对的提交 SHA**。`CONTRIBUTIONS.md` 只登记仓库地址与分支，不登记 SHA —— 不把无法验证的东西写成"真实提交"。
3. 本组自审（对照 PPT 全 27 页逐条复核）记录见下方。

## 本组自审记录

生成初版契约后，以 PPT 全部页面为清单逐条比对，发现并修复以下缺漏：

| 缺漏 | 判断依据 | 处理 |
| --- | --- | --- |
| DRAFT / REPAIR 的响应样例缺失 | PPT Slide 20、23 | 补齐到 `contract-examples.json` 的 `responses` |
| 运行期错误样例缺失（三个错误码无样例） | PPT Slide 9、Slide 16 第三轮 | 补 `errors` 三条 |
| REPAIR 输入缺构建脚本字段 | PPT Slide 23 | 增加 `makefile_uri` |
| 「产物怎样存储和下载」未给出**决定** | PPT Slide 11 明确列为"需要自己决定" | 写入 ADR-002（含读取步骤） |
| 「失败怎样处理」不完整 | PPT Slide 11 同上 | 写入 ADR-008 |
| 非法样例覆盖面窄（只有"缺 baseline"） | PPT Slide 26 | 扩到 6 类，新增"配置不匹配""版本不支持""delta 用错位置"等 |
| 缺 `CHANGELOG` / `CONTRIBUTIONS` / `STATUS` | PPT Slide 15 的提交材料与完成情况 | 补充三个文件 |

上述自审本身即为本表要求记录的"人工判断"证据：**AI 产出初版 → 人工以课程要求为基准复核 → 发现遗漏 → 修正并验证**。
