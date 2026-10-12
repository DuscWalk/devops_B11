# MDFixer · B11 本地原型

模块负责人王硕；胡博在 2026-10-12 授权 Codex 修复 E3 分支的源码损坏和接口回退，并补充实际验证。适配 [公共提交契约](../e2/task.schema.json)，只处理 MISSING，保留 REDUNDANT，过滤 RESOLVED。当前是本地主机执行的原型。

## 运行

仓库根目录需要 Python 3.10+、`e2/requirements.txt` 中的 jsonschema、Git、GNU Make 和 C 编译器：

```bash
.venv/bin/python mdfixer/validate_examples.py
.venv/bin/python mdfixer/demo.py
.venv/bin/python mdfixer/test_styles.py
.venv/bin/python e3/scripts/run_baseline.py
```

`demo.py` 从固定的源码 bundle 克隆临时项目，用 MANUAL 报告运行 REPAIR；检查补丁、三份产物、构建/测试和头文件变化后的重编译。`test_styles.py` 对四种风格运行真实 REPAIR，并覆盖隐式补丁插入后继续修复另一个目标的情况。统一入口包含全部模块回归和公共人工参考基线。

## 手动 CLI

先确认下列临时路径未被占用：

```bash
git clone fixtures/mdfixer-project/project.bundle /tmp/b11-md-project
.venv/bin/python mdfixer/mdfixer.py --local \
  --request mdfixer/examples/repair_request.json \
  --workspace /tmp/b11-md-project \
  --artifact-root fixtures/mdfixer-project/artifacts \
  --out-dir /tmp/b11-md-output > /tmp/b11-md-response.json
```

`--local` 表示在主机运行构建和验证命令，`input.image` 不用于启动容器。工作区 HEAD、Makefile URI 和报告 commit 必须一致，tracked 文件须干净。报告只能从指定 artifact root 下读取，不接受本地路径降级、路径穿越或指向根目录外的符号链接。每次候选验证都恢复原 Makefile，最终补丁需另行应用。

## 支持范围

| 风格 | 本轮支持的输入 | 修改 |
| --- | --- | --- |
| target | 唯一单目标规则，普通文件依赖 | 在依赖中追加缺失文件，保留续行和注释 |
| macro | 唯一的 `$(VAR)`，变量有一处字面文件列表定义 | 修改变量定义 |
| hybrid | 直接文件与唯一 `$(VAR)` 混合 | 修改变量定义，保留直接项 |
| implicit | `%.o: %.c`，单条 C 编译配方使用 `$<`、`-c`、`-o $@` | 补齐 `-MMD -MP`，加入 `-include <target>.d` |

变量定义支持 `=`、`:=`、`?=` 和续行的文本索引，不求值 Make 表达式。重复定义、`+=`、多个候选变量、嵌套变量、多目标/重复目标、歧义模式规则、条件分支及复杂 include 不猜测修复。共享变量的修改会影响引用该变量的所有规则，使用前需审阅。

每个 finding 至多生成一个候选，接受的修改累计后重新解析，避免后续行号失效。`max_iterations` 保留契约字段，未实现搜索迭代；`timeout_seconds` 限制每条构建/验证命令，不是任务总时限。

输出 `PATCH`、`STYLE_REPORT`、`TEST_RESULT`，记录实际构建/验证输出、候选统计与 SHA-256。`missing_fixed` 是接受候选的计数，不是检测器证明；重检始终为 `NOT_RUN`，不返回推算的 `recheck_missing_remaining`。

实现与证据见 [E3 模块记录](../e3/mdfixer-notes.md)。原 E2 作者、王硕 E3 扩展和胡博本轮修复均保留在 Git 历史中。
