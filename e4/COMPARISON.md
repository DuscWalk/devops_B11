# E4 三人复现与源码版本对照

2026-10-21。组长整合时重新读取三份原始证据，而非只采用个人 README 的结论。可在完整 Git 克隆执行 `python3 e4/verify_evidence.py` 重验。

| 项目 | 胡博 | 孙静怡 | 王硕 |
| --- | --- | --- | --- |
| 学号 | 241276007 | 241250112 | 241250110 |
| 源码版本 | 9765d57 | 9765d57 | 4b3fc1a |
| 工作区开始状态 | 干净 | 干净 | 干净 |
| 服务单测 | 4/4 | 4/4 | 4/4 |
| 冒烟构建退出码 | 1 | 1 | 1 |
| 冒烟关键失败 | make: not found | make: not found | make: not found |
| smoke passed | true | true | true |
| 原始完整构建日志与 JSON | 一致 | 一致 | 一致 |
| 文件/历史/镜像密钥检查 | 通过 | 通过 | 通过 |
| 假 Key 检出 / 清理后通过 | 已记录 | 已记录 | 已记录 |

三份 toolchain.lock 的 SHA256 均为 `ab4be6eeacdb753d1d2baf2475dc07613def30f7ccd5e8f88c127c2837e8aa05`，宿主 Docker/Compose/Buildx/Git/Make/Python 版本相同。成员镜像 ID、运行时间、磁盘空闲量有差异，符合手册允许的差异。构建共用同一服务器及 Docker 缓存，不属于三台独立机器的无缓存重建。

胡博与孙静怡按相同完整 SHA 复现，可直接用于课件要求的两人对照。王硕使用 4b3fc1a，后者比 9765d57 增加归档材料和保存属性；运行文件并未变化。核验命令：

```sh
git diff --exit-code 9765d5794fe43a0c5496be969004d3b84d5b740f 4b3fc1a318e1435750482826a140dda56aaa3457 -- Makefile compose.yaml .dockerignore .env.example requirements-dev.in requirements-dev.lock scripts services fixtures/draft setup
python3 e4/verify_evidence.py
```

该说明解释已发生的版本差异，不修改或伪造 source-sha.txt，也不把“运行代码一致”写成“完整提交相同”。本次整合和报告更新同样没有改变已实测的运行代码。

[机器对照和所有原始文件摘要](evidence/submission-20261021/member-comparison.json) 覆盖三个人的 62 份归档文件；同时核验胡博原清单 27 项和孙静怡原清单 20 项。王硕未提供个人摘要清单，本次在总表中计算其文件摘要，不补造其执行时的记录。以上核验是组长授权的机器审查，不新增相邻组或其他成员的人工签字。
