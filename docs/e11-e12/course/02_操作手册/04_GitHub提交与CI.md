# GitHub 提交与 CI

保留原仓库 main 和 E7/E8–E10 检查，在个人 e11-e12-integration 分支提交本次新增文件。

导入新工作流：

```bash
mkdir -p .github/workflows
cp "$E11_PACK/.github/workflows/e11e12.yml" .github/workflows/
printf '\ndata/\n' >> .gitignore
git add run_e11e12.py labs/e11e12 .github/workflows/e11e12.yml
git diff --cached --stat
git commit -m "Integrate E11 tracks and E12 artifact workflow"
git push -u origin e11-e12-integration
gh pr create --base main --head e11-e12-integration --title "E11-E12 integration" --body "增加轨道内集成、版本化报告、异步任务接口与实际产物联调。"
```

从输出读取实际 PR 编号，再整块执行：

```bash
read -r -p 'PR编号: ' PR
gh pr checks "$PR" --watch
```

工作流运行契约测试、E11-A、E11-B、E12，并归档 work/。组内 review 检查个人贡献、真实项目记录与失败处理；main 保留原有必需检查，并按课程安排增加 e11e12-integration。

data/ 中的本地实验项目和 work/ 大型记录单独归档；CI 自行运行 prepare 生成固定样例。真实项目提交和数据来源写入个人报告，在 PR 中给出证据路径。

代码导入前后保留原 E8–E10 文件。公共接口修改需同步更新 04_模板/接口契约.md 和对应测试。
