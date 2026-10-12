# MDFixer E3 模块交接

更新：2026-10-12。主责王硕；本轮由胡博明确授权 Codex 修复，操作和提交身份为 duscwalk。王硕此前提交四风格扩展和手动追踪说明；其中的源码损坏、接口回退和缺失运行证据由本轮补齐。机器验证不登记为组员人工复核。

## 本轮修复

- 恢复 Makefile 解析器，保留规则和变量续行的首行位置；匹配唯一显式规则或唯一模式规则。
- 恢复 Finding.origin、候选命令输出、显式 artifact root、URI 与符号链接边界校验、RESOLVED 过滤。
- 修复四风格补丁生成、可应用 unified diff、依赖注释/续行、隐式编译参数及 include 插入。
- 每次接受候选后重解析当前文本，修复累计补丁导致后续行号变化的问题。
- 恢复真实重检状态与命令输出，删除推算的 remaining 数量；仍为 LOCAL_PROTOTYPE，image_used=false。
- 把原来的四风格字符串比对改成 unittest 可发现的真实 REPAIR、补丁应用与构建测试，并补充有歧义输入的拒绝测试。

## 人工预期与运行验证

预期来自胡博的 [人工 fixtures](fixtures/README.md)，标记 B11_REFERENCE_ORACLE/MANUAL，未调用 A11 检测器。

```bash
.venv/bin/python -m unittest discover -s mdfixer -p 'test_*.py' -v
.venv/bin/python e3/scripts/run_baseline.py --export-evidence e3/evidence/你的新运行编号
```

模块测试覆盖：四风格生成结果与 Makefile.reference 字节一致；真实 REPAIR 接受候选；3 产物摘要正确；原 Makefile 恢复；git apply --check 和应用成功；构建后输出 1；修改 config.h 后不 clean 重编译输出 2。另有 implicit 插入后修复第二个目标的累计用例。公共参考基线独立保留旧值 1 / clean 2 / 修复后增量 3 的判据。

运行记录及本轮最终源码 SHA 见 [STATUS](STATUS.md) 和 [证据索引](evidence/README.md)。旧失败和旧成功记录按原版本保留，不用历史通过结果证明本次代码。

## 支持与拒绝范围

| 风格 | 支持范围 |
| --- | --- |
| target | 唯一单目标规则中的普通文件依赖，保留注释、续行、配方和 RD |
| macro / hybrid | 单个变量引用、唯一字面文件列表定义（= / := / ?=），支持变量续行 |
| implicit | 简单 %.o: %.c、单编译配方、$<、-c 和 -o $@，补齐 -MMD/-MP 和目标 .d include |

不求值复杂 Make 语义。多个变量、重复变量定义、+=、嵌套引用、多目标/重复目标、歧义模式规则、条件分支和复杂 include 不猜测修复。共享变量的更改会影响全部引用者；implicit 限于当前 C-to-object fixture，不声称覆盖任意模式规则。命令 timeout 是逐条限制，max_iterations 尚未实现迭代搜索。

missing_fixed 表示候选被 build/verify 接受的次数，不代表真实检测器重检。重检为 NOT_RUN，镜像未运行或交付 A11。

## 交接

王硕审阅修复后的支持/拒绝范围和真实结果；孙静怡复核 MDFixer，王硕复核 DRAFT，记录各自实际执行与人工结论。胡博归档这些记录，再确定正式提交版本与 E3 tag。本轮技术修复不代替 RV-01，也不要求提前进行 A11 联调。
