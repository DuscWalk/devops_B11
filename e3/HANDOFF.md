# E3 三人分工与交接

更新：2026-10-12。胡博已将 `fix/e3-mdfixer-baseline` 的修复及证据合入 main，保留原分支历史；[课件要求核对](REQUIREMENTS_CHECK.md) 已完成。公共基线与模块自动验收通过；DRAFT 的原有运行材料完整保留。当前任务是组员人工复核与正式提交整理，A11 不作为前置条件。

## 接收 main

先保存自己的改动，再拉取并在独立目录复跑：

```bash
git fetch origin
git worktree add --detach ../b11-e3-review origin/main
cd ../b11-e3-review
python3 -m venv .venv
.venv/bin/python -m pip install -r e2/requirements.txt
.venv/bin/python e3/scripts/run_baseline.py --export-evidence e3/evidence/你的编号-新运行
git rev-parse HEAD
```

工作树路径和导出目录须未被占用。可复用已有 Python 环境，不必重复安装。正式接收时使用正常 merge 或 MR，保留双方历史；不要将修复拆成零散 cherry-pick 或覆盖同伴未提交改动。

## 给孙静怡

DRAFT 的 fzy、失败/参考成功、Docker 与环境记录已归档，见 [DRAFT 记录](draft-notes.md)。

1. 审阅本人 DRAFT 的人工预期、构建与功能判据及实际日志。
2. 在新目录复核修复后的 MDFixer：运行公共入口，审阅四风格自动补丁与人工参考、头文件重编译、候选拒绝/恢复及支持边界。
3. 记录实际源码 SHA、环境、命令、结果和本人审阅结论，完成 RV-01 的 MDFixer 部分。

## 给王硕

此前四风格扩展已接收，本轮源码/接口修复及真实验证见 [MDFixer 记录](mdfixer-notes.md)。

1. 阅读修复后的解析器、补丁、runner 和测试，核对唯一变量、简单模式规则、拒绝歧义输入等边界。
2. 审阅四风格生成结果与 oracle、构建后的输出变化；参考输入仍为 MANUAL，不代表 A11 检测器已经运行。
3. 按 [DRAFT 复跑说明](draft-notes.md) 在新目录复核 DRAFT，检查缺工具链失败、参考构建和功能判据。
4. 交回本人实际复跑及人工结论，完成 RV-01 的 DRAFT 部分。

## 给胡博

技术修复、完整文档恢复、本地统一验收和干净检出证据已完成。已按胡博指令合入 main，供组员复核；合并不登记为人工复核或 LMS 提交。

1. 收齐两人的 RV-01 记录，处理实际发现的问题。
2. 后续若有新代码进入 main，针对差异复验；本轮已完成合并。
3. 最终提交时核对公共和 Docker 记录的版本、日期与适用范围；本轮未重新运行 Docker，现有记录来自 10 月 10 日。
4. 更新提交清单，确定正式 SHA/归档及 E3 tag，按 LMS 的格式和截止要求提交。

## 每人交回什么

- 分支或 MR、完整提交 SHA。
- 实际执行人、环境、固定源码版本、命令和退出码。
- 人工预期理由、实际输出及失败/恢复记录。
- 本人审阅结论、支持范围与剩余问题。

自动工具执行不代替人工复核。证据目录禁止覆盖旧运行；不提交 `.venv`、`e3/work` 或镜像 tar。

## 后续与 A11 对接

环境哈希算法与配置、镜像交付、ARTIFACT_ROOT 传输和接收日志、真实报告的源码位置、修复后的构建/测试/检测器重检，仍按后续课程阶段推进。本轮未发送消息或登记 A11 同意，重检保持 NOT_RUN。
