# STATUS

完成情况：已完成项、验证命令、输入、预期结果、实际结果；未完成项、失败原因与下一步。

## 已完成

验证命令统一为：`python validate.py`

| 项目 | 输入 | 预期结果 | 实际结果 |
| --- | --- | --- | --- |
| 四类创建请求校验 | `contract-examples.json` → `requests` | 四类请求均通过 | 通过（4/4） |
| 受理响应（202） | `responses.accepted_202` | 只需 `job_id` + `status=QUEUED` | 通过 |
| 查询响应（含产物引用） | `responses.query_*` | 满足完整 Job（`input` 回显 + `output` 产物） | 通过（4/4） |
| 非法 `job_type` | `job_type=ABC` | 被拒绝 | 被拒绝（`VALIDATION_4001`） |
| 缺少 `baseline` | `INCREMENTAL_CHECK` 无 baseline | 被拒绝 | 被拒绝（`VALIDATION_4001`） |
| 缺少 `build_environment_hash` | `INCREMENTAL_CHECK` 无环境哈希 | 被拒绝 | 被拒绝（`VALIDATION_4001`） |
| 基线配置不一致 | `baseline.configuration_id ≠ input.configuration_id` | 被拒绝 | 被拒绝（`VALIDATION_4001`） |
| 基线配置缺失 | `input` 无 `configuration_id` 或 `baseline` 无它 | 被拒绝 | 被拒绝（`VALIDATION_4001`） |
| **负向对照校验（15 种）** | 由 `validate.py` 第二部分当场执行：篡改**完整合法样例**且**只改一处**，期望被拒绝 | 全部被拒绝 | **15/15 全部被拒绝**，任何人可当场复算 |
| 基线提交不一致 | `baseline.commit ≠ base_commit` | 被拒绝 | 由校验器规则覆盖（检查 06） |
| 版本不支持 | `schema_version=2.0.0` | 被拒绝 | 被拒绝（`VALIDATION_4001`） |
| `delta` 用错位置 | `FULL_CHECK` 响应含 delta | 被拒绝 | 被拒绝（`CONTRACT_4002` + 400 —— 属协议层违反，不是服务端崩溃） |
| 检测发现 ≠ 执行错误 | 同时含 `error` 与 `output.findings` 的响应 | 被拒绝 | 由校验器规则覆盖（检查 04） |
| `delta` 结构 | `responses.query_incremental_check.output.delta` | 含 `baseline_commit` + `added`/`removed`，每项带 `declared` | 通过 |
| RD（冗余依赖）样例 | `findings` 含 `type=REDUNDANT` | 校验通过，且 `evidence` 语义正确 | 通过 |
| 建议修复字段 | `findings[*].suggested_fix` | 存在且为字符串 | 通过 |
| 产物 URI 格式 | 全部 `artifact://` 引用 | 符合 `artifact://<group>/<job_id>/<name>` | 通过 |
| 标准 Schema 交叉校验 | `task.schema.json`（jsonschema 库） | 请求与响应均满足正式 Schema | 通过（9/9） |

**汇总**：`python validate.py` → **42 项全部通过，退出码 0**（零依赖部分 33 项 = 契约检查 18 + 负向对照 15；`jsonschema` 可选部分 9 项）。

> 说明：此前版本本条写的是「独立负向对照 13 项」，但那是用**临时脚本**跑的，跑完即删 —— 评审指出「包里找不到执行它的东西，无法复算」。现已把负向对照**做进 `validate.py` 第二部分**，项数由 13 扩到 15，随包可复算。

## 未完成

| 项目 | 原因 | 下一步 | 负责人 |
| --- | --- | --- | --- |
| 与 B11 的接口协商 | 尚未与配对组当面确认 | 课堂三轮交换练习：环境/基线 → MD 报告 → 失败输入 | A11、B11 |
| 产物实际互读验证 | 共享目录路径未定 | 确定 `ARTIFACT_ROOT` 后由 B11 实际读取一次依赖图 | A11、B11 |
| `CONTRIBUTIONS.md` 组内分工与协商结论 | 需与 B11 课堂协商 | 协商后回填分工、结论与 Issue/PR（提交 SHA 待仓库可推送后再补） | A11 |
| C2 提交与链式检测 | C2 尚未选择 | 选定 C2 后验证 C1 → C2 的增量检测链 | A11 |
| MDFixer 补丁端到端验证 | 依赖 B11 实现 | 使用固定 MD 报告联调 | B11 |

## 已知局限（如实记录）

| 项目 | 说明 |
| --- | --- |
| `delta` 是否退化为 findings 复述 | 属**语义**问题，结构校验无法自动判定，由 `ADR.md` ADR-006 约束 |
| 强制降级保护 | 未定义"缺 baseline 时自动降级为全量检测"的行为，本设计选择**直接拒绝**而非静默降级 |
| 多版本并存 | 202 受理响应不含 `schema_version`，查询响应含；若未来需多版本并存需重新评估，见 `ADR.md` ADR-003 |
| 环境哈希的具体算法 | 只约定字段存在与语义（同一环境应产出同一哈希），未约定哈希计算方式 —— E3 与 B11 确认 |
