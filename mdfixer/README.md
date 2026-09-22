# MDFixer — B11 组 E2 阶段实现

负责人：王硕。公共契约与提交状态见 [E2 总入口](../e2/README.md)。

修复 Makefile 中**缺失依赖（MISSING）**的自动化工具，与 A11 组 E2 契约（`task.schema.json` v1.1.0）适配。

## 目录结构

```
mdfixer/
├── mdfixer.py                 # CLI 入口：解析参数、调用 run_repair、输出响应
├── mdfixer_core.py            # 数据模型 + URI 解析 + MD 报告加载
├── mdfixer_engine.py          # Makefile 解析 + 声明风格检测
├── mdfixer_patch.py           # 补丁生成 + 统一 diff
├── mdfixer_verify.py          # 命令执行 + 候选验证
├── mdfixer_runner.py          # run_repair 主流程编排
├── validate_examples.py       # 契约校验脚本（零依赖）
├── README.md                  # 本文件
└── examples/
    ├── repair_request.json         # REPAIR 请求样例
    ├── repair_response_sample.json # REPAIR 响应样例
    ├── md_report.json              # MD 报告样例（含 MISSING / REDUNDANT）
    └── Makefile                    # 演示用 Makefile（app 目标缺失依赖）
```
## 功能说明

对应 B11 组 `e2/Backlog.md` 中 MDFixer 任务：

1. **读取 MD 报告**：从 A11 组产出的 MD 报告中提取 `findings`，只保留 `type=MISSING` 的发现（`REDUNDANT` 不进入修复流程，见 ADR-004）。
2. **解析 Makefile**：识别所有规则（`target: prerequisites`），支持续行符和变量展开。
3. **生成候选补丁**：将缺失依赖追加到对应 target 的依赖列表，保持现有声明风格。
4. **验证补丁**：对每个候选补丁执行 `build` + `verify`，通过则接受，失败则记录拒绝原因。
5. **输出产物**：
   - `PATCH`（统一 diff）
   - `STYLE_REPORT`（声明风格 + 修复统计）
   - `TEST_RESULT`（候选接受/拒绝详情）

## 与 A11 契约的对齐

| 契约字段 | 本实现 |
|----------|--------|
| `schema_version` | `1.1.0` |
| `job_type` | `REPAIR` |
| `input.repository` | `{url, commit}` |
| `input.md_report_uri` | `artifact://<group>/<job_id>/<name>` |
| `input.makefile_uri` | `repo://<sha40>/<path>` |
| `input.build.command` | 构建命令 |
| `input.verify_command` | 验证命令 |
| `output.patch_uri` | `artifact://b11/<job_id>/fix.patch` |
| `output.patch_sha256` | 补丁内容 SHA-256 |
| `output.artifacts` | PATCH / STYLE_REPORT / TEST_RESULT |
| `output.summary` | 候选统计 |

## 使用方法

### 1. 运行修复

```bash
python mdfixer.py --request examples/repair_request.json --out-dir out/
```

输出 REPAIR 响应 JSON 到 stdout，产物（patch、style_report、test_result）写入 `--out-dir`。

### 2. 契约校验

```bash
# 校验请求
python validate_examples.py --request examples/repair_request.json

# 校验响应
python validate_examples.py --response out/response.json

# 同时校验
python validate_examples.py --request examples/repair_request.json --response examples/repair_response_sample.json
```

## 设计决策

- **只修 MISSING**：REDUNDANT 依赖的移除风险较高，E2 阶段暂不处理（ADR-004）。
- **增量验证**：每个 MISSING 候选补丁独立 build+verify，接受的补丁累积到最终 patch。
- **声明风格保持**：解析现有 Makefile 规则，追加依赖时不改变原有格式（空格分隔、续行符等）。
- **URI 降级**：E2 阶段允许直接传本地文件路径作为 `artifact://` 解析失败时的降级。

## 依赖

仅使用 Python 3.10+ 标准库，无第三方依赖。
