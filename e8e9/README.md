# B11 E8–E9 可复现入口

按课程 B 轨完成固定 MD 报告、direct/macro/mixed 候选和源文件保护。
原版 `lab.py` 未改；`b11_handoff.prepare_candidate()` 增加本组输入边界，返回 diff、plan、receipt。
全部 25 项测试由 `unittest discover` 收集，包括课程原有 7 项以及三人的新增用例。

```bash
# 在自己的干净克隆和对应镜像就绪后执行；不要求修改全局 Git 身份
E8_IMAGE=course-e8e10:241276007 bash e8e9/run.sh
python3 e8e9/verify.py "$(cat work/last-e8e9-B.path)"
```

`run.sh` 每次新建 work 目录，禁网容器以宿主普通 UID 运行，记录镜像、工具链、源码 SHA、
各命令及退出码。依次运行全部测试、原版和个人接口的 E8/E9，不覆盖旧 OUT。
样例 Git 历史通过 `.bundle` 保存，因此归档排除 `.git` 后仍可核对内部 SHA。
`verify.py` 在本机重算归档哈希、从 bundle 恢复样例，并把补丁应用到临时副本与整文件预期比较。

接口限制：只接受课程 schema/profile、干净且与报告提交匹配的本地样例，MD 文件必须跟踪且
解析后的路径在项目内。用于单人顺序实验，没有实现并发文件修改隔离；也未证明报告内容可信。
不支持完整 Make 语法、复杂隐式规则或论文完整 DIS/LLM。集成入口合并重复 MD，拒绝修改具有多个显式引用的变量；课程基线保留用于影响对照。
原文件干净、补丁可应用仅是 E8/E9 判定，不能替代 E10 构建与行为正确性验证。

最终分工及验收见 [STATUS.md](STATUS.md)。[HANDOFF.md](HANDOFF.md) 保存最初的任务分配。

逐项要求、此次发现的遗漏与补正结果见 [REQUIREMENTS_AUDIT.md](REQUIREMENTS_AUDIT.md)。
旧归档核验须显式加 `--legacy`；默认核验要求包含 E9 共享变量练习。
