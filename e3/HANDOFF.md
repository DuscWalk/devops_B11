# E3 三人分工与交接

更新：2026-10-10。胡博的公共基线 `feat/e3-hubo-baseline` 已合入孙静怡的 `feat/draft`，DRAFT 运行材料归档提交为 `98dae53`。公共与 DRAFT 的已完成结果见 [STATUS](STATUS.md)。MDFixer 新模块交接、人工交叉复核、最终整合尚待完成；A11 不作为 E3 独立样例准备的前置条件。

## 接收步骤

孙静怡已在 `feat/draft` 接收公共分支，无需重复创建分支。王硕和胡博接收本轮材料时，先保存自己的改动，再拉取远端并审阅：

```bash
git fetch origin
git log --oneline origin/feat/draft -10
```

在各自任务分支正常合并已审阅的交接分支，处理冲突后验证。不要用 cherry-pick 拆散公共代码与证据依赖，也不要覆盖未提交改动。

## 给孙静怡

已完成：固定 fzy 版本、公共本地与 Docker 复跑、缺 make 的失败样本、参考修复及断网构建/功能验证、环境与失败日志归档，见 [DRAFT 记录](draft-notes.md)。DR-01/DR-02 的运行材料已齐。

1. 本人阅读人工预期、修复理由与实际日志，确认能解释编译成功和功能成功两个判据；将人工审阅结论补入模块记录。
2. 向组内交回 `feat/draft` 与完整 SHA、模块说明和证据路径。组员接收前不标记其已验收。
3. 王硕提交 MDFixer 材料后，在新目录复跑并审阅四风格参考、原型边界及失败恢复；记录实际复核人、环境、命令和结论，完成 RV-01 中自己的部分。
4. 自动 DRAFT 和镜像真实交付 A11 属后续阶段，E3 不必等待。

## 给王硕

1. 运行 `.venv/bin/python e3/scripts/run_baseline.py`，检查已有固定源码 bundle、MD 报告和原型执行。
2. 检查 `e3/fixtures/mdfixer/` 四风格人工答案、Patch 应用、头文件无 clean 重建和无效候选恢复。
3. 明确自动原型支持范围：当前是简单显式规则；Macro/Hybrid/Implicit 的参考成功不能记作工具已经支持。若扩展实现，在自己的分支追加对应实际输入输出。
4. 主要修改 `mdfixer/` 和新建 `e3/evidence/mdfixer-你的运行标识/`；在 `e3/mdfixer-notes.md` 记录模块结论，交回后由胡博整合公共文档。
5. 不删 RD，不把 MANUAL/ORACLE 当 A11 检测结果；检测器重检仍标 NOT_RUN。
6. 交回分支/SHA、模块记录和新证据后，交叉复核 DRAFT：按 [复跑说明](draft-notes.md) 在新目录执行，审阅缺工具链失败、参考构建和功能判据，留下本人复核结论。

当前公共验证已运行 E2 原型，但不等于王硕已经完成上述 E3 工作。四风格重点核对：修复前改头文件仍输出旧值 1，clean 后输出 2；参考修复后再次改头文件无需 clean 即输出 3；无效候选应拒绝并恢复原文件。

## 给胡博

1. 审阅孙静怡新增的公共脚本修正（Windows 超时、draft 源码快照）和 Tiny Greeting 官方 APT HTTPS 调整，核对其回归与输入追溯证据。
2. 接收 DRAFT、MDFixer 两份模块说明、分支/SHA 和证据；检查人工预期理由、实际结果与支持范围没有混淆。
3. 收齐孙静怡与王硕的 RV-01 交叉复核记录；有问题则退回对应负责人修正后复验。
4. 合并已审阅的模块分支，在最终提交上运行公共入口并记录 Docker 验证；将最终环境、源码 SHA 和证据归档。
5. 核对 STATUS、Backlog、CONTRIBUTIONS 和 SUBMISSION，按课程要求整理固定提交或归档及 E3 tag。当前只是进度同步，HB-07 尚未完成。

## 每人交回什么

- 分支/MR 链接与完整提交 SHA。
- 执行人、实际环境、固定项目版本、可重新执行的命令。
- 人工预期与判断理由，实际输出/退出码，失败与恢复日志。
- 已支持、未支持、卡点、试过什么和下一步。

E3 运行证据导出示例：

```bash
.venv/bin/python e3/scripts/run_baseline.py --export-evidence e3/evidence/你的编号-新运行
```

结果目录必须不存在。先看 `summary.json`，再看 `observations.json` / `commands.json` 和原始日志；不提交 `e3/work/`、虚拟环境或镜像 tar。

## 后续给 A11 的待确认清单

`e3/environment-hash.md` 的规范字段与算法；配置和 baseline 一致性；镜像交付方式；`ARTIFACT_ROOT` 实际传输及接收日志；真实 report 的源码/Makefile 位置；修复后的构建、测试、检测器重检分别记录。此处是沟通材料，未发送消息、未登记 A11 同意。
