# E8–E9 个人实验报告

学号：241276007；小组：B11；轨道：B / MDfixer；原角色：接口与联调。
仓库：<https://github.com/DuscWalk/devops_B11>；分支：`student/241276007/e8-e10`；
公共导入 PR [#10](https://github.com/DuscWalk/devops_B11/pull/10)，个人 PR [#11](https://github.com/DuscWalk/devops_B11/pull/11)。

## 运行与版本

- 原版 7 项测试源码：`5e6372d7e5eb061f3b44d2b016cbc3f5bc52418c`。
- 本次实际测试和 E8/E9 源码：`5920735c0e785b6994f055f09a33ecd65818e933`。
  随后的报告、证据提交用于归档，不倒写为原运行源码 SHA。
- 学院服务器：Linux x86_64，普通用户 duscwalk / UID 1000，内存实际可见约 1.7 GiB，无 swap。
  2 GB 配置成功构建未修改的课程 Dockerfile；实验在 `--network none` 容器运行。
- 镜像：`course-e8e10:241276007`；实际 ID：
  `sha256:fe4f9564f5856532361da04a9f11073fb093bd6dc2a5fa138725a190a3aa3653`。
- 记录的工具链：Python 3.13.14、GCC 元包 4:14.2.0-1、GNU Make 4.4.1-2、Git 2.47.3、strace 6.13、amd64。
  完整软件包版本见证据 `toolchain.lock`，不声称 apt 未固定版本的安装能逐字节重建。
- 实际时间：2026-11-17 07:33:03–07:33:06 UTC（本地 2026-11-16）。
- 外层目录：`/home/duscwalk/241276007/e8e9-b11-20261116/repo`。
- 命令：`bash e8e9/run.sh`，生成 `work/e8e9-B.tLP54Uq5`；
  `python3 e8e9/verify.py work/e8e9-B.tLP54Uq5` 成功。
- 归档位置：`e8e9/evidence/cloud/e8e9-B.tLP54Uq5`，原构建及 7 项基线测试在相邻目录。
  运行时的内层 `.git` 不提交，8 个 sample bundle 保留对应 Git 历史。

## 按要求逐项判定

|实验 / 场景|输入、独立预期|实际结果与证据|
|---|---|---|
|E8 固定报告|main.o 应缺 config.h，冗余 unused.h；helper.o 无错误|`personal-e8/fixed-md-report.json` 精确匹配；报告来自本次 GCC -MM，不是 A11 服务|
|E8 候选|只给 main.o 增加 config.h；保留 RD 和 recipe|`candidate.patch`、`patch-plan.json` style=direct；apply check 成功，全部跟踪文件哈希和 Git 状态不变|
|E8 旧报告|报告 commit=40 个 0 应拒绝|`stale-input.json`、`expected-failure.json`：STALE_REPORT，源字节保持|
|E9 direct|目标行增加 config.h|`personal-e9/direct-input.json`、`direct.patch`、`direct-plan.json` 及原 direct 项目|
|E9 macro|只改 DEPS；main.o 仍引用 $(DEPS)|对应 macro 三份产物及原项目；在额外 `apply-demo` 中应用，整份 Makefile 与明确预期一致|
|E9 mixed|保持 HEADERS 定义和引用；给目标行增加 config.h|对应 mixed 三份产物及原项目；配方及 RD 保持|
|E8 自主扩展|HEAD 相同但头文件已修改，应拒绝；越界 symlink、未绑定提交的依赖和错误报告也应拒绝|`test_b11_handoff.py` 中 7 项 E8 测试全部通过；其中明确先证明原 patch 接受脏输入，再验证新接口拒绝|
|E9 自主测试|三种风格各有 config.h 和 extra.h 两条 MD，保留其余全部字节；第二目标无效不得部分写回|同文件 2 项 E9 测试分别覆盖 3 种风格，全部通过；预期是手工给定目标行/变量行替换和完整文件字节|

原基线和个人接口在不同的 `baseline-e8/e9`、`personal-e8/e9` 目录重跑。
所有五个步骤（测试及四次实验）的退出码均为 0；16 项测试包括未改的课程 7 项及个人 9 项。
本机下载后重算 146 个文件哈希，从 bundle 克隆样例，核对内部 SHA 和原输入，应用补丁到临时副本，
与整文件预期比较；验证通过。E8/E9 候选生成不包含 E10 构建、功能测试、动态重检及回滚验收。

内部样例提交（与外层学生源码提交用途不同）：

|样例|内部 SHA|
|---|---|
|E8 project|`2d8ac9fc41f4f2b6a14a6d91c62697d8a48580f7`|
|E9 direct|`af49589aeff7f069f0741b24505722a33914eafe`|
|E9 macro|`73497f792dd02b27fcf5a31e5dd2d96b42b6c7d1`|
|E9 mixed|`17dcac95af7266cff7f578add48ea58ad0aa09f6`|

baseline 与 personal 样例在同一秒由相同 fixture 生成，可能有相同内部 SHA；它们是不同目录，
对应日志、命令和模式分别保存，不能据此将外层源码 SHA 与样例 SHA 混用。

## 本人新增与论文机制

课程 `lab.py`、原 7 项测试和环境源码保持原样，来源逐文件摘要见 `docs/e8-e9/source-manifest.json`。
新增 `b11_handoff.prepare_candidate()` 校验 schema/profile、commit、干净工作区、依赖路径和提交归属，
再调用原 patch；返回候选、可解释计划和源文件摘要，不直接落地修改。
新增 `run_b11_evidence.py` 按详细 B 手册保存完整输入和计划，补齐一键 demo 不保存 E9 输入报告的问题；
`run.sh` 和 `verify.py` 负责日志、镜像/源码绑定及异地复核。CI 保留原 E7 检查和课程兼容演示，
增加个人测试及可下载证据。

MDfixer 论文思想在此体现为定位声明、保持已有声明结构并生成候选。direct 改目标，macro 改变量定义，
mixed 保留宏并改目标。本次只是两个 C 翻译单元、项目内头文件、显式 Make 规则和简单变量的教学子集；
未实现完整声明图距离/DIS、隐式/模式规则、递归 Make、LLM 修复。共享变量跨目标影响由核心负责人继续扩展；
本人的 E9 用例验证多 MD 的结构保持，不冒充共享变量算法。代码运行不调用外部模型服务。

## CI、协作和未完成项

首次实现 SHA `4c08be3d6a4e98156ee488c1098a36f622a3369b`（15 项测试）的 push 检查：
[E8/E9 与教学兼容检查](https://github.com/DuscWalk/devops_B11/actions/runs/44038866461)，
[E7 回归](https://github.com/DuscWalk/devops_B11/actions/runs/44038866602)，均成功。
原始 artifact `e8e10-evidence-44038866461` 下载并与 GitHub API digest 比对，归档于
`e8e9/evidence/ci/44038866461`。最终报告提交的 PR 检查在 PR 页面及本地交接包中另附，不将旧 run 说成新 head。

追加修复后的源码 `5920735c0e785b6994f055f09a33ecd65818e933`（16 项测试）的 PR 检查：
[E8/E9 检查](https://github.com/DuscWalk/devops_B11/actions/runs/44039585738) 和
[E7 回归](https://github.com/DuscWalk/devops_B11/actions/runs/44039585595) 均成功；
对应 artifact 与 API 元数据在 `e8e9/evidence/ci/44039585738`。
PR 的实际 checkout 为 GitHub 临时合并提交，`trigger.json` 记录的 head_sha 才是个人分支源码；
归档分别保留二者并核对，未将临时合并 SHA 误当个人提交。

公共导入 PR #10 已经用户确认后合并，main 为 `cee2486e78bfb10f20be5f5ca608252bcff1a080`。
个人 PR #11 等待审阅；组员还需各自完成代码、运行及报告，
任务详见 `e8e9/HANDOFF.md`。这些是全组提交前事项，不能把本人实跑等同三人已交付。
无需等待 A11；后续真实跨组报告需单独适配验证。E10 另做，CI 的参考演示不算个人 E10 报告。

身份说明：用户确认本次新提交使用 `241276007 <241276007@smail.nju.edu.cn>`，
已用于追加修复、同步及后续报告提交。确认前的公共导入和首次实现按原全局 duscwalk 身份，保留其真实历史，
没有强制推送重写旧提交。服务器独立克隆的 local user.name 已设为本人学号，全局设置保持原样。
自编入口显式选择镜像，也可以使用课程 run_lab.py/classroom_helpers.sh 的数字学号入口。
