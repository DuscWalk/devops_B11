# MDFixer — B11 组 E2/E3 阶段实现

修复 Makefile 中**缺失依赖（MISSING）**的自动化工具，与 A11 组 E2 契约（`task.schema.json` v1.1.0）适配。E3 阶段扩展支持四种 Makefile 声明风格。

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
├── test_styles.py             # E3 四风格补丁比对脚本
├── mdfixer-notes.md           # E3 模块交接说明
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
                         
                         ## 声明风格支持（E3）
                         
                         MDFixer 自动检测并修复以下四种 Makefile 声明风格：
                         
                         | 风格 | 原声明示例 | 修复策略 |
                         |------|-----------|----------|
                         | **target** | `main.o: main.c unused.h` | 直接在规则依赖行追加缺失头文件 |
                         | **macro** | `DEPS = main.c unused.h` + `main.o: $(DEPS)` | 在变量定义中追加缺失头文件 |
                         | **hybrid** | `HEADERS = unused.h` + `main.o: main.c $(HEADERS)` | 在头文件变量中追加，保留直接项 |
                         | **implicit** | `%.o: %.c` + `$(CC) $(CFLAGS) -c $< -o $@` | 配方追加 `-MMD -MP`，插入 `-include <target>.d` |
                         
                         判定依据：规则目标含 `%` → implicit；依赖全为 `$(VAR)` → macro；依赖混合直接文件与变量 → hybrid；其余 → target。
                         
                         ### 本地风格比对
                         
                         ```bash
                         python test_styles.py
                         ```
                         
                         对四种风格分别比对生成结果与 E3 参考 `Makefile.reference`，全部一致则输出 `ALL PASS`。
                         
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
                         - **声明风格保持**：解析现有 Makefile 规则，追加依赖时不改变原有格式（空格分隔、续行符等）。E3 阶段扩展支持 target / macro / hybrid / implicit 四种风格。
                         - **变量解析**：解析 `=` / `:=` / `?=` / `+=` 变量定义，macro/hybrid 风格在对应变量中追加依赖。
                         - **implicit 自动依赖**：模式规则通过 `-MMD -MP` 生成 `.d` 文件并 `-include`，不硬编码头文件名。
                         - **URI 降级**：E2 阶段允许直接传本地文件路径作为 `artifact://` 解析失败时的降级。
                         
                         ## 依赖
                         
                         仅使用 Python 3.10+ 标准库，无第三方依赖。
                         # MDFixer · B11 本地原型

负责人王硕；胡博在 E2 提交整合时修复语法/接口和演示。适配 [公共提交契约](../e2/task.schema.json)，功能范围为显式简单 Makefile 规则的缺失依赖补丁；不是完整论文复现或已部署服务。

## 一键演示

仓库根目录（Python 3.10+、jsonschema、Git、Make、C 编译器）：

```bash
.venv/bin/python mdfixer/validate_examples.py
.venv/bin/python mdfixer/demo.py
```

演示从仓库内 project.bundle 克隆完整固定源码，不联网；读取明确标 MANUAL 的混合报告，仅修 app.o 缺少 config.h 声明，保留 legacy.h。验证补丁能应用、构建/测试通过、修改头文件后重编译。原型输出 PATCH、STYLE_REPORT、TEST_RESULT；重检标 NOT_RUN，未运行 A11 检测器。

保存新执行证据可用 `--evidence-dir /tmp/b11-md-evidence`；已提交的真实结果在 [e2/evidence/mdfixer-2026-09-22/](../e2/evidence/mdfixer-2026-09-22/)。

## 手动 CLI

先将 fixture bundle 克隆到独立工作区，再运行：

```bash
git clone fixtures/mdfixer-project/project.bundle /tmp/b11-md-project
.venv/bin/python mdfixer/mdfixer.py --local \
  --request mdfixer/examples/repair_request.json \
  --workspace /tmp/b11-md-project \
  --artifact-root fixtures/mdfixer-project/artifacts \
  --out-dir /tmp/b11-md-output > /tmp/b11-md-response.json
```

临时目标路径应未被占用。输出目录按 b11/job_id/name 存储，响应为完整 REPAIR Job。CLI 显式 --local 表示在当前主机运行请求内构建命令，**不会使用 input.image 启动容器**。工作区 HEAD、Makefile URI、报告 commit 必须对应，tracked 文件应干净。候选验证后恢复原 Makefile，最终补丁需另行应用。

## 模块

| 文件 | 职责 |
| --- | --- |
| mdfixer.py | Schema 校验、CLI、完整 Job 输出 |
| mdfixer_core.py | 数据模型、URI、报告解析和 MISSING/RESOLVED 过滤 |
| mdfixer_engine.py | 简单显式规则索引与风格特征 |
| mdfixer_patch.py | 添加声明、生成可应用 unified diff |
| mdfixer_verify.py | 限时命令、候选验证及原文件恢复 |
| mdfixer_runner.py | 版本匹配、候选流程、产物及统计 |
| validate_examples.py / demo.py / test_mdfixer.py | 标准契约检查、实际执行演示、6 个回归 |

## 支持边界

支持简单显式规则和续行，追加依赖时保留配方与已有 RD；变量展开、模式规则、多重同名目标、复杂 include 等不猜测修复。每个 finding 生成一个候选，不实现搜索迭代；max_iterations 仅保留契约字段。timeout_seconds 在当前原型限制每条构建/验证命令，不是整个任务总时限。构建成功不等同于工具重检，缺少重检时不返回伪造的 remaining=0。

来源初版为王硕 feat/mdfixer 97fb979；胡博整合修正保留 Git 追溯。原初版示例使用占位 SHA/无源码与不完整 Job，当前替换为可复现教学项目；人工来源和固定版本见 [fixture README](../fixtures/mdfixer-project/README.md)。
