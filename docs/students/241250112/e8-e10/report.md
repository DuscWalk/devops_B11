# E8–E9 个人实验报告：241250112

姓名：孙静怡。轨道：B / MDfixer。范围：E8、E9 与交叉验证；本报告不声明完成 E10。

## 本人完成的内容

- 在个人服务器目录与个人镜像中运行 E8、E9 的 B 组课程实验，保存固定 MD 报告、候选补丁、补丁计划、过期报告拒绝结果及三种声明样例。
- 新增 `labs/e8e10/test_cross_review.py`：验证仅有 RD 的报告不会删除依赖，输入 `Makefile` 字节和 Git 跟踪文件保持不变；复现共享 `DEPS` 变量使未请求的 `helper.o` 增加 `config.h` 冗余依赖。
- 新增 `labs/e8e10/cross_review_evidence.py`：对 direct、macro、mixed 分别留存原始输入报告、样例提交号、补丁、计划、`git apply --check` 与输入文件 SHA256；仅在额外副本应用共享变量补丁。
- 将 CI 的 unittest 发现范围改为 `test_*.py`，使新增交叉测试参加质量门禁。

课程原有 `lab.py`、`test_profile.py`、`run_lab.py` 是公共基线，非本人新写。`e9-B-241250112-20261118` 是课程一键演示；`cross-review-241250112-20261118` 是本人补充的独立输入与影响证据。

## 真实环境与运行

服务器：`119.3.234.250`；个人目录：`/home/duscwalk/devops-students/241250112/draft`。镜像：`course-e8e10:241250112`，镜像 ID：`sha256:354c97a4bfadc4b2fe0d44a46e8f41303b9883d944f6ba3f59ed77dcce2b6959`。工具版本见证据中的 `toolchain.lock`。

本次服务器实验使用从 GitHub `main` 的 `cee2486e78bfb10f20be5f5ca608252bcff1a080` 导出的课程代码子集，服务器另行初始化的本地仓库提交为 `2a2550d2fd1673dacdaa0cc9de633d54ebe4701e`；两者不是同一个 Git 提交。证据中的 `student-source-commit.txt` 是后者，`student-source-status.txt` 记录服务器仓库的跟踪文件无改动。样例项目的提交号分别保存在各输入报告及 `e9-cases.json` 中。

在服务器上执行：

```bash
python3 run_lab.py build
python3 run_lab.py e8 --track B --out work/e8-B-241250112-20261118
python3 run_lab.py e9 --track B --out work/e9-B-241250112-20261118
docker run --rm --network none --user 1000:1000 -e HOME=/tmp \
  -v "$PWD:/course" -w /course -e PYTHONPATH=/course/labs/e8e10 \
  course-e8e10:241250112 python3 -m unittest discover \
  -s labs/e8e10 -p 'test_*.py' -v
docker run --rm --network none --user 1000:1000 -e HOME=/tmp \
  -v "$PWD:/course" -w /course -e PYTHONPATH=/course/labs/e8e10 \
  course-e8e10:241250112 python3 labs/e8e10/cross_review_evidence.py \
  --out /course/work/cross-review-241250112-20261118
```

结果：E8 与 E9 均输出 `COMPLETED`；9 项单元测试通过，退出码 0。E8 补丁计划只为 `main.o` 增加 `config.h`，过期报告返回 `STALE_REPORT`。E9 direct、macro、mixed 三例均通过 `git apply --check`，各原输入 `Makefile` 的 SHA256 前后相同，Git 跟踪文件干净。

共享变量反例的样例提交号为 `bb241edc0956c9df8091d4bb892a27fcfe493226`。报告只请求补 `main.o/config.h`；补丁编辑 `DEPS` 后，额外副本的 `helper.o` 也声明了 `config.h`，而 GCC 实际依赖中没有它，扫描产生新的 `REDUNDANT/helper.o/config.h`。这表明共享变量补丁必须先检查全部引用目标，当前课程基线不具备该限制。

## 证据与边界

原始输出、输入样例、补丁、计划、样例 Git bundle、测试日志均在 `e8e9/evidence/personal-241250112-20261118/`。同目录 `evidence.tar.gz` 的 SHA256 为 `18a384cb6aee7d96e167763634e9a4edb504d5c5cff3f00399758c37756f4d8f`。bundle 保存样例提交历史；展开文件不含嵌套 `.git`。

截至本次取分支，MDFixer 负责人 `student/241250110/e8-e10` 的最新提交 `da3f0fb` 只新增 `test_profile.py` 中的个人用例，尚无约定的扩展修复入口。因此这里验证的是课程基线及共享变量风险，不能声称已验证尚未提交的扩展。待该入口出现后，应以本测试与 `shared-input.json` 再跑一次，并核验拒绝或局部修复策略。
