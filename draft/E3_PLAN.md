# E3 工作核对与下一步

核对日期：2026-10-10。范围：B11，孙静怡负责 DRAFT、王硕负责 MDFixer、胡博负责公共验收与整合。本文是当前材料审阅，不登记尚未进行的成员复跑或人工确认。

## 课件依据与阶段边界

已阅读仓库根目录 `E3_并行测试基线.pptx` 全部 39 张幻灯片，SHA-256 为 `dee364f71c39f8c57526dcd4e46a97741d330db6c1e928d615dc208b8b9a930e`。本地课件与胡博分支 `docs/E3_并行测试基线.pptx` 字节一致。以下按实际幻灯片顺序编号，课件页脚有跳号。

- 第 2–4、6–9 页：准备固定项目、环境、预期结果和判断依据，保存命令、真实输出、失败和个人贡献。
- 第 8 页：DRAFT 需同时证明编译成功（退出 0、可执行文件存在）与功能验证成功（退出码及预期输出），不能只看镜像建成。
- 第 29–32 页：DRAFT 失败 Dockerfile 缺 make/C 工具链，保存非零退出与可定位日志；参考修复补工具链，同一项目在容器输出 `hello E3`。Tiny Greeting 是课程示例，项目也可自行选择。
- 第 33–37 页：MDFixer 固定 MD 报告与 Makefile、四类声明风格参考补丁、修复前后行为、无效候选拒绝及恢复。修复后再次改头文件、不 clean 就应重建。
- 第 10 页：E4 环境/密钥、E5 BuildChecker/DRAFT、E8 EChecker/MDFixer、E12 真实数据联调。完整自动 DRAFT、异步 API 和 A11 镜像接收不能列为 E3 的必需完成条件。

之前会话把实际镜像交付和自动服务放在紧接 E2 的待办里；现按 E3 课件重新排序：先完成独立测试基线和组员交叉复核，不等待 A11 或自动工具实现。

## 仓库同步结果

- 当前工作分支仍为 `feat/draft`。原先有一场未完成的合并，目标为 `origin/main` 的 `ac19b744b5b12bdb98ab1ac7c2374d612f768b32`。
- 唯一未解决文件为 `e2/CONTRIBUTIONS.md`。本地 `a93bc0a` 只将待认领改为三人姓名，远端完整贡献表已包含相同姓名并新增成果及 SHA，因此保留完整表。没有删除或重写本地提交。
- 合并提交 `8f178f2` 已将最新 main 纳入当前分支。E2 总校验已实际重跑并退出 0：20 项公共回归、6 项 MDFixer 回归、模块样例、实际修复演示及 8 产物读取通过。
- 已 fetch 胡博 E3 分支；其 tip 为 `d994302b43b123d4967c63894d6ddb572b2fbb0a`，尚未合入 main，也尚未合入本分支。阅读/核验该分支不等于合并或本人成员复跑。
- 根目录本地 PPT 已单独加入 `.gitignore`，文件保留。胡博分支已有受 Git 跟踪的 docs 课件归档，本次未移除它；ignore 不会自动取消已有跟踪。

## 成员已完成什么

| 成员 | 可核查成果 | 所在版本与边界 |
| --- | --- | --- |
| 孙静怡（你） | fzy 固定 SHA、DRAFT 接口/产物样例、WSL 与 Docker 基线；31 测试、99 断言日志；真实镜像信息 | E2 的 `65704cb`、`d7bca1e` 已集成到 main。本轮没有重新运行 Docker，也没有确认 9 月镜像今天仍在本机 |
| 王硕 | MDFixer 解析、补丁、验证、编排及 CLI 初版，固定 MD/REPAIR 样例 | 分支 tip `97fb979`，已集成 main；胡博后续修复集成问题。当前自动原型只支持简单显式规则；没有查到王硕新的 E3 模块交接提交 |
| 胡博（E2） | 正式 Schema/OpenAPI、协议确认记录、来源保留、总校验、人工固定项目 bundle、MDFixer 集成修复与真实演示 | main `ac19b74`；本次已复跑 E2 验证通过。A11 确认的证据边界见 e2/AGREEMENT.md |
| 胡博（E3） | 课程整理、Tiny Greeting、四风格人工参考、统一入口、环境指纹提案、文件读取/损坏拒绝、Docker 验收、交接说明 | E3 分支 `d994302`；归档记录本地 67/67、Docker 3/3、基础设施回归 5/5，不能相加为独立测试总数 |

胡博证据核验：本次从 Git 对象读取并重新计算 271 个归档文件摘要，全部一致；读取 local/Docker summary，与 STATUS 声明相符。未在本机重新执行 E3 入口。参考补丁通过不代表 MDFixer 自动支持 Macro/Hybrid/Implicit，胡博执行也不代表孙静怡/王硕已复核。

固定版本入口：[E3 README](https://git.nju.edu.cn/devops_b11/devops-project-b11/-/blob/d994302b43b123d4967c63894d6ddb572b2fbb0a/e3/README.md)、[交接说明](https://git.nju.edu.cn/devops_b11/devops-project-b11/-/blob/d994302b43b123d4967c63894d6ddb572b2fbb0a/e3/HANDOFF.md)、[任务清单](https://git.nju.edu.cn/devops_b11/devops-project-b11/-/blob/d994302b43b123d4967c63894d6ddb572b2fbb0a/e3/Backlog.md)。

## E3 剩余待办

| 优先级 / 编号 | 负责人 | 工作 | 完成标准 |
| --- | --- | --- | --- |
| P0 接收公共分支 | 全体协作 | 审阅胡博 E3 分支后合入工作分支或 main | 获得完整 fixtures/scripts/evidence，保留原贡献与历史；不重复编写已有公共脚本 |
| P1 DR-01 | 孙静怡 | 复跑 fzy，检查原镜像是否仍可用，必要时重建 | 固定源码 SHA、实际工具链、可执行文件、构建与功能验证结果、新日志及镜像 ID |
| P1 DR-02 | 孙静怡 | 复跑 Tiny Greeting 的 broken/reference Docker；补 fzy 适用故障和修复依据 | 非零失败确为缺工具链且可定位；同一项目参考修复后功能输出正确；Dockerfile diff/日志/退出码保留 |
| P1 MF-01 | 王硕 | 复核固定 MD 报告和四种声明风格人工答案 | 来源标记清楚，版本对应，Patch 可应用；修复前旧值 1、clean 2，修复后改头文件、不 clean 输出 3 |
| P1 MF-02 | 王硕 | 复跑原型，补支持/拒绝范围和恢复证据 | 简单显式规则实际通过；未支持风格如实拒绝，不把人工参考 Patch 当自动结果；无效候选恢复后可构建 |
| P2 RV-01 | 孙静怡、王硕交叉复核；胡博整合 | 在新目录按 README 复跑，审阅对方预期答案 | 明确执行者、完整提交、环境、命令、输出与未完成项；不覆盖旧证据 |
| P2 最终交付 | 胡博汇总，全体供材料 | 汇总模块记录、贡献、提交入口和 E3 状态 | 每人分支/提交、预期与实际结果、失败/恢复、限制均可追溯 |

**DRAFT 特别注意：** 9 月保存的 Docker Hub 认证超时属于网络故障，不能充当课件要求的缺 make/C 工具链失败。已有 fzy 成功证据可以继续保留，但需要新的 E3 复跑记录及明确的失败/参考修复对照。

## 你下一次开始时的步骤

1. 先接收胡博的 E3 公共分支。当前分支本轮已同步 main；在工作区干净、审阅公共分支后，可正常 `git merge origin/feat/e3-hubo-baseline`。也可等该分支通过组内审阅合入 main 后同步 main。不要强制 reset 或拆散公共证据做 cherry-pick。
2. 在 Linux/WSL 准备 Python 3.10+ 和 `e2/requirements.txt`，运行公共本地基线，再运行 Docker 基线。
3. 以自己的新标识导出记录，例如以下路径必须尚不存在（命令只在接收公共分支后可运行）：

```bash
.venv/bin/python e3/scripts/run_baseline.py --export-evidence e3/evidence/draft-sjy-20261010-local
.venv/bin/python e3/scripts/verify_docker.py --export-evidence e3/evidence/draft-sjy-20261010-docker
```

4. 复跑自己的 fzy 基线并补故障对照；在 `e3/draft-notes.md` 写 DRAFT 结论，主要改 draft/ 和自己的新证据目录，公共 STATUS/Backlog 交胡博整合。
5. 与王硕交换复核，再交回分支/MR、SHA、实际结果和限制。本文件日期只是整理日期，上述命令尚未由本次审阅执行。

## 后续阶段保留事项

自动生成/多轮修正属于 E5 DRAFT；复杂 Makefile 自动修复属于 E8 MDFixer；A11 真实镜像/产物接收、真实报告和检测器重检属于后续尤其 E12 联调。环境指纹目前仍是 B11 提案。它们均不能被此次本地基线检查自动判为完成。
