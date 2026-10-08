# 胡博 → 组员交接

分支：`feat/e3-hubo-baseline`。胡博完成的是课件整理、公共验收底座、证据管理、环境指纹提案与统一集成验证。模块分工延续 E2；A11 不作为独立样例准备的前置条件。

## 接收步骤

先保存自己的改动，再拉取远端，不使用强制 reset：

```bash
git fetch origin
# 选择尚未存在的本地分支名
git switch -c feat/e3-draft origin/feat/e3-hubo-baseline
# 王硕对应使用 feat/e3-mdfixer
```

如果已在自己的任务分支，不要执行上述 switch；先由本人决定提交/暂存现有修改，再正常合并公共分支。不要用 cherry-pick 拆散公共代码与证据的依赖。

## 给孙静怡

1. 阅读 `docs/E3_要求整理.md` 和 `e3/README.md`，运行本地公共入口及 Docker 入口。
2. 沿用 `draft/PROJECT.md` 的固定 fzy SHA；核对自己的镜像可用性、配置和编译器，不以胡博主机环境替代 fzy GCC13。
3. 保存自己实际执行的失败/成功构建、验证命令、镜像 ID/基础 digest、包版本和输出。公共 Tiny Greeting 是参考验收样本，可先复跑，再补自己的 fzy 材料。
4. 主要修改 `draft/` 和新建 `e3/evidence/draft-你的运行标识/`；在 `e3/draft-notes.md` 记录本模块结论，交回后由胡博整合公共 STATUS/Backlog。
5. 镜像真实传给 A11 和自动 DRAFT 属后续阶段，E3 不必等待它们。

## 给王硕

1. 运行 `.venv/bin/python e3/scripts/run_baseline.py`，检查已有固定源码 bundle、MD 报告和原型执行。
2. 检查 `e3/fixtures/mdfixer/` 四风格人工答案、Patch 应用、头文件无 clean 重建和无效候选恢复。
3. 明确自动原型支持范围：当前是简单显式规则；Macro/Hybrid/Implicit 的参考成功不能记作工具已经支持。若扩展实现，在自己的分支追加对应实际输入输出。
4. 主要修改 `mdfixer/` 和新建 `e3/evidence/mdfixer-你的运行标识/`；在 `e3/mdfixer-notes.md` 记录模块结论，交回后由胡博整合公共文档。
5. 不删 RD，不把 MANUAL/ORACLE 当 A11 检测结果；检测器重检仍标 NOT_RUN。

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
