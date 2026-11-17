# E8–E9 分工与交接

适用仓库：<https://github.com/DuscWalk/devops_B11>，轨道 B / MDfixer。
分工依据：`CONTRIBUTING.md`、`e2/Backlog.md`、`e3/HANDOFF.md`；延续模块责任，
本次按课程要求每人另交个人代码、个人运行及报告。以下是任务安排，不能算已完成贡献。

## 分支与当前入口

公共导入：`teaching/e8-e10`，PR <https://github.com/DuscWalk/devops_B11/pull/10>。
接口与证据实现：`student/241276007/e8-e10`。
公共导入尚未合并，不能认为 `main` 已有 E8 代码。可先阅读导入 PR 和本文件、准备个人环境；
正式按课程流程运行前，由组长合并公共导入，随后执行：

```bash
git status --short              # 有修改先自己保存，不覆盖
git fetch origin
git switch main
git pull --ff-only origin main
# 用自己的数字学号替换 SID，只在自己的克隆设置身份
SID=本人学号
git config --local user.name "$SID"
git config --local user.email 本人已验证邮箱
git switch -c "student/$SID/e8-e10"
```

这里 `origin` 指 GitHub；已有双远端仓库应先 `git remote -v`，GitHub 如名为 `github`，
将上述 fetch/pull 对应改为 github，**不要误用 GitLab main**。已有个人分支用 switch 后合入 main，
不要强制重建。各人使用自己的克隆、目录和认证；禁止借用别人的提交身份。

## 三人任务

|原角色 / 个人分支|E8 本人完成|E9 本人完成|交付位置|
|---|---|---|---|
|接口与联调 / `student/241276007/e8-e10`|公共环境与固定报告；提交号、干净输入、路径边界；拒绝证据|三种声明输入/补丁/计划完整归档；多 MD 整文件保持和原子拒绝测试|`labs/e8e10/b11_handoff.py`、`test_b11_handoff.py`、`e8e9/`、本人报告|
|MDFixer / `student/241250110/e8-e10`|亲自完成 B 手册；新增重复 MD 报告场景，明确重复输入预期|新增自己的修复入口及测试：重复依赖只添加一次；分析共享变量被多个目标引用时的影响，选择明确拒绝或局部修复并给证据|建议独立 `labs/e8e10/mdfixer_extension.py`、`test_mdfixer_extension.py`、本人报告|
|DRAFT、交叉验证 / `student/241250112/e8-e10`|亲自完成 B 手册；RD-only 或未知目标反例，字节与 Git 状态前后对比|独立验证 direct/macro/mixed；测试多目标或共享变量影响，手工写预期，验证 MDFixer 负责人的扩展；保存失败及修复后的真实运行|建议 `labs/e8e10/test_cross_review.py`、本人报告|

MDFixer 负责人独立模块可调用 `lab.patch()` 或自行实现受限规则，避免直接覆盖课程原始
`lab.py`。提供公开函数签名（建议 `patch(project, report) -> (diff, plan)`），接口负责人随后
接入 `prepare_candidate`。交叉验证负责人可以先测试原基线；核心扩展到位后补一次新的 OUT。
两人均不得仅复制第三人的日志或将一个 review 评论作为全部个人工作。

## 每人完成清单

1. 按 `docs/e8-e9/course/02_操作手册/00_公共准备.md` 建个人镜像和分支；共享 2 GB 服务器
   首次构建串行。已实测本机容量可构建课程原镜像，不需为本次实验升级配置。
2. 完成 `8_E8_B组.md` 全部步骤：原项目、固定报告、candidate.patch、plan、旧报告拒绝、
   `git apply --check`、源字节和状态；加自己的 E8 用例，用新 OUT 重跑。
3. 完成 `9_E9_B组.md`：三份独立输入报告、原项目、三份 patch/plan；在额外副本应用 macro；
   自主扩展/测试也要实际重跑。必须保留三份输入，不能只交一键演示的 diff。
4. 在镜像内运行原 7 项和自己的测试。若用本分支公共脚本：

   ```bash
   E8_IMAGE="course-e8e10:$(git config --local user.name)" bash e8e9/run.sh
   python3 e8e9/verify.py "$(cat work/last-e8e9-B.path)"
   ```

   公共导入 main 初期没有 `e8e9/run.sh` 时先用课程手册；不要等待脚本阻塞个人工作。
5. 写 `docs/students/<本人学号>/e8-e10/{report.md,ADR.md,AI_USAGE.md}`，明确哪些是课程代码、
   本人新增什么、AI 辅助了什么、真实命令及结果、学生源码 SHA 和内部样例 SHA。
6. 推个人分支、开 PR 到 main、等待 E7 和 e8e10 检查；下载真实 Actions artifact。
   回复组长：分支、PR、源码 SHA、两次实验 OUT、证据包 SHA256、结果和未覆盖范围。

## 组长收齐后的验收

核验每人的真实提交/报告/独立测试和证据，保留作者历史，接入核心扩展并运行交叉测试。
合入 main 前核对最终 PR head 的两个 CI 检查，确认无失败或混用旧证据后再生成小组提交包。
本文件不把任务分配当作验收完成；人员状态见 `STATUS.md`。

B 组本次固定输入由 GCC -MM 生成，不需 A11 提供服务或批准教学接口；真实跨组适配属于后续集成。
E10 构建、测试、重检和回滚不在本次个人完成声明中。
