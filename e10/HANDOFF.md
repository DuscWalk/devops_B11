# B11 E10 交接：候选验证与回滚

三人分别在自己的 `student/<学号>/e8-e10` 分支完成 B 组手册的三次事务，在自己的新 OUT 做自主任务，提交个人 PR。实验输入使用本地固定 MD；A11 的服务适配属于后续集成。组长等三人实跑、报告、PR 检查和交叉验收齐全再整合。

| 负责人 | 本次要交什么 | 验收时看什么 |
|---|---|---|
| 胡博 241276007（集成、证据） | 三次事务与 BuildChecker；增加能构建、功能正确但引入新 MD 的拒绝用例；归档 CI 与源文件证据 | 四项检查通过，仅 `no_missing=False`；报告定位到 `helper.o/helper.c`；原项目跟踪文件全部保持 |
| 王硕 241250110（MDFixer） | 在自己的分支运行三次事务；从本人候选生成/修复入口设计编译失败案例，可用能应用但带错误编译参数的候选；调整候选后在新副本重试 | 保留两份候选和原始输入；坏候选 `patch_applies=True`、无成功 build、日志有编译失败原因、源字节不变；修复后五个检查通过。补自己的回归测试 |
| 孙静怡 241250112（交叉验证） | 在自己的分支运行三次事务；独立验证接受后再拒绝时仅正确的 Makefile 保留；另做编译失败或残余 MD 自主反例。取王硕的原样例和候选跨分支复核 | 以接受前后字节副本和文件哈希作独立预期；区分初始版本与已接受版本。记被复核 SHA、自主测试、OUT 以及各事务实际结果 |

**开始**：沿用本人原 GitHub 克隆和个人分支，从当前 `main` 合入 E8/E9 已验收内容。工作区须干净，`git config --local user.name` 为本人学号，镜像为 `course-e8e10:<本人学号>`。两人可以立即独立开始，只有最后交叉复核依赖王硕的候选。

```bash
git fetch origin
git switch "student/$(git config --local user.name)/e8-e10"
git merge --no-edit origin/main
```

**实操**：按 `docs/e8-e9/course/02_操作手册/10_E10_B组.md` 第 0–12 节，从新 OUT 保存输入报告、plan、candidate.patch、source-before/after-accept、三次 validation/sandbox、results.csv、gate.json 及动态重检。测试失败和坏补丁是预期拒绝，阶段命令应退出 0。另存自主场景的失败原因、预期与实际、源字节对照和新增测试日志。个人报告、ADR、AI_USAGE 延续 `docs/students/<本人学号>/e8-e10/`，保留 E8/E9 原记录。

**交回组长**：个人分支及 PR、运行时外层源码 SHA、样例内部 SHA、镜像 ID、OUT、证据压缩包和 SHA256、与 PR head 对应的通过 run/artifact。报告明确预期、实际和限制。未完成时保留草稿 PR。组长核对三人的原始证据、E7 与 E8–E10 检查后再合并。
