# E3 公共验收样例

来源：胡博授权 Codex 依据 E3 课件重新编写，标记 `B11_REFERENCE_ORACLE`。没有读取教师实验包，不能使用 `INSTRUCTOR_ORACLE` 或声称这些文件是教师原文件。人工预期在各目录 `oracle.json`；实际运行输出单独在 `work/` 和导出的 `evidence/`。

## DRAFT

`draft/tiny-greeting/` 含源码、Makefile、故意缺工具链的 Dockerfile 和人工参考成功 Dockerfile。构建 `make`，验证 `./hello`，输出必须精确为 `hello E3\n` 且退出 0。主仓提交 SHA 加目录路径、逐文件摘要固定源码；基础镜像 tag 和 APT 包尚未固定版本，每次记录解析后的镜像 ID/digest 与包清单。

fzy 沿用 `draft/PROJECT.md` 的固定完整 SHA 和双层验证。Tiny Greeting 是公共验收的离线小样例，不能代替孙静怡的 fzy 模块运行或 A11 的真实环境使用。

## MDFixer 四种声明

每个目录含 `main.c`、`config.h`、`unused.h`、`Makefile.before`、`Makefile.reference`、`reference.patch`、`oracle.json`。默认编译选项 `-O0 -Wall -Wextra`；只考察当前构建的项目头文件，不把系统头文件算作人工发现集合。

| 样例 | 原声明 | 参考修改 |
| --- | --- | --- |
| target | `main.o: main.c unused.h` | 直接追加 `config.h`，保留 RD |
| macro | `main.o: $(DEPS)` | 在 `DEPS` 中追加 `config.h` |
| hybrid | `main.o: main.c $(HEADERS)` | 保留直接项，在 `HEADERS` 中追加 `config.h` |
| implicit | `%.o: %.c` | 配方增加 `-MMD -MP`，增加 `-include main.d` |

每例行为：初始输出 1；只将头文件改为 2，未修复增量仍输出 1；clean 后输出 2；应用参考 Patch 后 clean 输出 2；再次改为 3，不 clean 应输出 3。无效候选加失败 recipe，现有 `verify_candidate` 必须拒绝并恢复原 Makefile，再次构建输出 3。

Target/Macro/Hybrid 保留 `unused.h` 声明作为不自动修 RD 的约束。Implicit 检查编译生成 `main.d` 中的 `config.h`。这些是独立的参考答案测试。2026-10-12 修复后的自动原型另有四风格 REPAIR / 构建回归，复用本目录的字节预期，但不将其当作真实检测结果；支持范围见 [模块记录](../mdfixer-notes.md)。

现有原型的真实 REPAIR 输入沿用 `fixtures/mdfixer-project/` 的固定 bundle SHA、报告和来源；不是上面四个样例的伪造服务响应。
