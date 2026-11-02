# 孙静怡 E5 复现报告

## 身份与目标

- 学号：241250112；邮箱：241250112@smail.nju.edu.cn；B11 / B 轨道 DRAFT。
- 日期：2026-11-02（北京时间）。执行方式：本人授权 Codex，经本人 SSH 密钥登录，以共享 Linux 用户 `duscwalk` 在独立目录运行。自动执行不等于本人逐项人工审阅。
- 服务器目录：`/home/duscwalk/241250112/e5-20261102`。
- 小组仓库：`https://git.nju.edu.cn/devops_b11/devops-project-b11.git`；本次分支 `feat/e5-draft-reproduction`，交付 SHA 从该分支 Git 历史查询。
- 服务器教学参考源码本地提交：`9cb50ab71ff0c0ef8ccb2420a2c5e26afb37f470`。这是从 ZIP 初始化的独立参考快照提交，不是小组远端的提交；可核对的实际使用文件和摘要均已归档。

目标是串起“真实构建失败 → 错误/项目上下文提示 → 修复候选 → 实际构建 → 程序运行”的单次流程，解释每个结论如何对应原始证据。

## 输入与环境

输入为课程 Tiny Greeting C 样例。Makefile 使用 `cc main.c -o hello`，运行 `./hello` 的预期输出为 `hello E3\n`。不是论文基准项目，也不是 E2/E3 的 fzy。

初始及所有候选保留同一基础镜像：

```text
python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
```

服务器 Ubuntu 22.04.5，2 核、1.7 GiB 内存，Docker 29.1.3；完整环境见 [doctor.log](evidence/sun-jingyi-20261102/preflight/doctor.log)。原始自检退出 1，原因是内存低于新包要求的 4 GiB。本次保留失败并尝试小样例，**构建成功不等于服务器通过资源验收**。没有更改 doctor 阈值、全局 Docker 配置、他人工作区或缓存。

## E5 实际过程

1. 从原始学生 ZIP 提取 B 轨道至个人新目录，设置仓库本地学号身份，提交未修改的参考源码。ZIP 摘要及脚本/fixture 摘要见 [来源清单](evidence/sun-jingyi-20261102/source/manifest.json)。
2. 执行 `python3 scripts/lab_cloud.py e5 --out work/e5-01 --build-timeout 600`。Docker build 返回 1，RUN 层缺 make 返回 127；采集与提示生成成功，E5 驱动脚本返回 0。这三个退出码描述不同层次，不混为一谈。
3. 读取两份实际生成的提示。本次 Codex 在同一会话看到完整提示后生成两份 Dockerfile，并在对话中输出；每份代码块原样保存为 `model-response.txt`。没有独立 API 调用、没有调用 DeepSeek，也没有把包内历史回复登记为本次生成。
4. 错误驱动候选显式安装 `make gcc libc6-dev`；上下文驱动候选安装 `build-essential`。二者保留固定 FROM、WORKDIR、COPY、RUN make、CMD。选择上下文驱动候选，因为标准工具包覆盖 C 构建所需依赖；错误驱动候选仅保存比较，未实际构建，不宣称它已经通过。
5. 原选中候选使用默认 Debian HTTP 源。158.34 秒期间软件包索引下载长时间无新日志，主动中止这次 buildx，构建返回 130。该结果不是工具链故障，不计为候选成功。保留完整日志及中止说明。
6. 单独派生 `context-driven-mirror`：保持基础 digest 和项目指令，仅将 Debian 源改为华为 HTTPS 镜像并增加索引下载超时/重试参数。保留 Debian 签名验证，不禁用 TLS 校验。此项属于 Codex 后续操作调整，原始回复不改写，差异另存。实际构建耗时 88.75 秒、退出 0。
7. inspect 本次成功构建的镜像，按完整 ID 启动；禁网、2 CPU、1 GiB、256 PID 限制、30 秒外层预算。实际退出 0，stdout 精确为 `hello E3\n`。使用 `--rm`，随后 inspect 原容器 ID 证实容器已不存在。

完整记录见 [证据入口](evidence/sun-jingyi-20261102/README.md)。镜像标签 `course1020-draft-e5:241250112`，本次 image ID：

```text
sha256:57dfd1ba5f0438ef068a2f42f0d0a315f32cf02e040be68d21de5b4b9ee2eeca
```

该镜像仅存在于服务器 daemon，未发布到 registry。基础层可能复用共享缓存，不宣称无缓存构建。APT 软件包未逐版本锁定，实际版本见 `verification/toolchain.txt`。

## 与论文流程的对应和边界

| 论文方法/课程目标 | 本次做法与限制 |
| --- | --- |
| 构建失败驱动修复 | 真实执行 Docker build，保存完整输出和 make 缺失位置；网络下载中止独立记录 |
| 错误驱动、上下文驱动提示 | 教师脚本依据本次日志产生两种提示；context 版本额外提供项目 README |
| 模型生成与候选选择 | 本会话 Codex 生成两份候选，人工规则选择；不是独立模型对照实验，也未实现论文自动选择算法 |
| 构建与功能双层成功 | 先 build=0，再运行该次 image ID，exit=0 且精确输出匹配 |
| 大规模项目评估 | 本次仅课程 Tiny Greeting，不声称复现论文成功率、耗时结论或 3–5 个提高项目 |
| 自动服务 | 本次为 E5 分步复现，不登记 E6 MVP、24 项服务测试或 E7 故障门禁已完成 |

## 下一步交接

- 孙静怡本人阅读本报告、候选来源和日志；组长接收本分支。
- 组长/助教确认 E5 资源要求，必要时扩容后重新自检。原始 FAIL 记录不删除。
- E6 可将 `candidates/context-driven-mirror/Dockerfile` 作为自己的已保存候选，连同 provenance 和差异一起交接；不要标成包内 DeepSeek replay。
- E6/E7 后续应重新构建服务镜像并执行各阶段验收，本次没有执行它们，也没有建立 GitHub 仓库、发送组间消息或提交 LMS。
