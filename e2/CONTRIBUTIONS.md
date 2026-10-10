# B11 成员贡献与版本

| 成员 | 职责与实际贡献 | 可核对提交 |
| --- | --- | --- |
| 孙静怡 | DRAFT Q03/Q07 回复；固定 fzy 提交；请求/202/成功失败样例；5 文件；WSL 与手工 Docker 构建/31 测试日志 | `65704cb66c1b84709569e6d5eca044838dff9722`、`d7bca1e7a6143e39f29164c9b43fde7824b0def5`；Git 作者 hotori，成员对应关系由胡博确认 |
| 王硕 | MDFixer 核心、解析/补丁/验证/编排模块、CLI、MD/REPAIR 样例与校验器初版 | feat/mdfixer 最新 `97fb9798a9ba30751db8305cd2d7411a2b5f6c36`；历史作者 王 硕 <241250110@smail.nju.edu.cn>，原始提交全部保留 |
| 胡博 | 公共契约来源核对、Schema/校验/读取器、A11 对接、DRAFT 复核、整合修复 MDFixer、可运行人工样本、文档/验证/提交包 | `4f88d13a126608854a5ba7ac062d169af4780e75`、`95ea87c35b4126c134b1403a168a4f18ba9d402e` 及本次整合提交；作者 duscwalk <241276007@smail.nju.edu.cn> |

## 集成过程

- DRAFT 合并提交 `7bb2242`，MDFixer 合并提交 `41ae268`，均保留成员历史。仅 README 发生内容冲突，保留模块成果并补负责人和统一入口。
- 王硕分支有上传拆分/测试临时文件的历史，最终树不存在那些临时文件；没有压缩或重写成员历史。
- 本次新增修复由胡博负责、Codex 辅助：换行转义、URI/版本匹配、完整 Job、候选恢复、有效 diff、命令超时、重检如实报告，具体见 CONTRACT_REVIEW。
- A11 原 Schema/样例/脚本归 A11，来源 `96f35cc175d12f51f3f7f0915ba35a98d303fcb3`；9 月 22 日复核其 `8b0c3b9142cb379547e429e310c1b3b0bb9ccd34` 核心协议文件未变。本组不将来源内容计作原创。

## 版本与证据

本次正式整合修复提交为 `578280a`（`feat(e2): finalize confirmed B11 submission and repair validation`）；最终提交通过 `git rev-parse HEAD` 核对，发布标记和 LMS 入口见 SUBMISSION。仓库提交记录本身是作者/时间/说明证据；本轮采用本地合并并推送，没有创建或虚构 Issue/MR 链接。

验证见 STATUS 与 evidence。孙静怡 Docker 构建日志是其环境执行记录，胡博复核摘要；本次 MDFixer 演示是胡博本机真实运行。所有技术成果可追溯到具体文件和提交，人工确认来源单独记录在 AGREEMENT。
