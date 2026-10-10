# MDFixer E3 模块交接

日期：2026-10-11。负责人：王硕；本次由 AI 助手按用户授权在该工作区执行。
以下是机器执行结果，不代表孙静怡、胡博或 A11 已人工复核。

## 已完成

| 任务 | 结果 | 证据 |
|------|------|------|
| MF-01 四风格参考核对 | target / macro / hybrid / implicit 四种声明风格的参考补丁、oracle 预期逐一核对 | e3/fixtures/mdfixer/*/oracle.json、reference.patch |
| MF-02 原型扩展 | 在原有 target 风格基础上，实现 macro / hybrid / implicit 三种风格的自动补丁生成 | mdfixer_engine.py、mdfixer_patch.py |
| 风格检测 | 新增 `detect_rule_style()`，依据规则目标是否含 `%`、前缀是否仅变量引用、是否混合直接文件判定风格 | mdfixer_engine.py |
| 变量解析 | 新增 `VariableDef` 数据类与变量定义解析，支持 `=` / `:=` / `?=` / `+=` | mdfixer_core.py、mdfixer_engine.py |
| 证据留档 | `declaration_style.json` 新增 `rule_styles` 与 `variables` 字段，记录每条规则的判定风格和变量定义 | mdfixer_runner.py |

## 四风格实现说明

每种风格的修复策略与 E3 参考补丁一致：

| 风格 | 原声明示例 | 修复策略 |
|------|-----------|----------|
| target | `main.o: main.c unused.h` | 直接在规则依赖行追加 `config.h` |
| macro | `DEPS = main.c unused.h` + `main.o: $(DEPS)` | 在 `DEPS` 变量定义中追加 `config.h` |
| hybrid | `HEADERS = unused.h` + `main.o: main.c $(HEADERS)` | 在 `HEADERS` 变量定义中追加 `config.h`，保留直接项 |
| implicit | `%.o: %.c` + `$(CC) $(CFLAGS) -c $< -o $@` | 配方追加 `-MMD -MP`，并插入 `-include main.d` |

### 判定逻辑

- **implicit**：规则目标含 `%`（模式规则）。
- **macro**：规则依赖全部为 `$(VAR)` 变量引用。
- **hybrid**：规则依赖同时含直接文件和 `$(VAR)` 变量引用。
- **target**：其余情况（显式文件依赖）。

### 关键约束

- 保留 `unused.h` 声明，不自动修 RD（REDUNDANT）。
- implicit 风格中 `.d` 文件名由 finding 的 target 推导（`main.o` → `main.d`）。
- 若依赖已存在，不重复添加。
- 参考成功（oracle）是人工答案，不等于检测器已重检；检测器重检仍标 `NOT_RUN`。

## 支持范围

### 已支持

- 单目标显式规则（target）的依赖追加。
- 单变量依赖规则（macro）：在变量定义中追加依赖。
- 混合依赖规则（hybrid）：在头文件变量中追加依赖。
- 模式规则（implicit）：注入 `-MMD -MP` 与 `-include <target>.d`。
- 行内变量解析（`$(VAR)`）、简单赋值运算符。

### 未支持 / 已知限制

- 多目标规则（`a b: dep`）仅按第一个目标匹配。
- 续行符（`\`）依赖追加仅处理单行尾部续行，未处理中间续行插入。
- `$(VAR)` 嵌套或 `$${VAR}` shell 转义不解析。
- `:=` 立即展开变量的递归展开不做语义求值，仅按文本追加。
- implicit 风格假定 `.d` 文件与目标同名（`<target>.d`），未处理 `$(basename ...)` 等派生。
- 复杂 Makefile（条件分支 `ifeq`、`include` 其他 Makefile、`define` 多行变量）未覆盖。

## 验证

由于本机沙箱无可用 Python 解释器（WindowsApps 为 Store 存根、WSL 未安装），四种风格的补丁生成通过逐行手动追踪与 E3 参考 `Makefile.reference` / `reference.patch` 比对，结论一致：

- target：`main.o: main.c unused.h` → `main.o: main.c unused.h config.h`
- macro：`DEPS = main.c unused.h` → `DEPS = main.c unused.h config.h`
- hybrid：`HEADERS = unused.h` → `HEADERS = unused.h config.h`
- implicit：配方加 `-MMD -MP`，插入空行 + `-include main.d` + 空行

本地测试脚本 `test_styles.py` 已随代码提交，在有 Python 的环境（WSL / Linux）执行 `python3 test_styles.py` 可复现四风格比对。

## 交回内容

- 修改：`mdfixer_core.py`（新增 `VariableDef`）、`mdfixer_engine.py`（变量解析、`detect_rule_style`）、`mdfixer_patch.py`（四风格补丁）、`mdfixer_runner.py`（适配新签名、扩展 style_report）。
- 新增：`test_styles.py`（四风格本地比对脚本）。
- 本说明文件。

## 仍待处理

- 王硕本人人工复核四风格参考与原型输出。
- RV-01：孙静怡复核 MDFixer；王硕复核 DRAFT（按 HANDOFF 操作）。
- 胡博接收本模块、合并并运行公共入口 `e3/scripts/run_baseline.py`，归档证据至 `e3/evidence/mdfixer-<编号>/`。
- 真实检测器报告与重检（NOT_RUN）、A11 接收属后续阶段，不阻塞本次 E3 交接。
