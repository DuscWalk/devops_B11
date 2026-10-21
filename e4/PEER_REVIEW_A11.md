# B11 对 A11 的 E4 README 复现记录

2026-10-21，胡博（241276007）提供 A11 地址，Codex 在胡博授权下执行检查，Git 身份为胡博学号，系统用户 duscwalk。方向为 **B11 检查 A11**；尚未收到 **A11 检查 B11** 的反馈。

## 仓库与执行环境

A11 地址：`git@git.nju.edu.cn:devops-group11/devops-group11.git`。固定 main 提交：`b45d2d5ba9f04ac24276e54b5f0e0c5c4bac8c78`。操作入口是 `e4/README.md`，根目录没有 README.md。

使用 HuaweiDevOps 上独立目录 `/home/duscwalk/241276007/a11-e4-review-20261021`。本地 SSH 克隆成功；云端 HTTPS 克隆需要认证，因此传输包含已克隆历史的 Git bundle 后克隆并固定 SHA；bundle 摘要已归档，没有复制私钥。按 README 设置仓库局部 Git 身份，补装用户级 uv 0.9.5。PyPI 下载缓慢后通过华为 PyPI 镜像完成安装，安装日志均保留。

执行时 PATH 加入用户工具目录，PS1 设为空以避开服务器非交互 Bash 启动警告。没有修改 A11 已跟踪源码、提交或推送；运行生成的 work 目录未被 A11 忽略，因此工作区状态出现未跟踪的证据目录，不能写成运行后完全干净。

## 三次尝试分别记录

### 第一次：执行者过早中断，不作为复现失败结论

执行 `make all`，doctor 成功，固定 digest 的基础镜像拉取成功。构建日志随后未刷新，Codex 未检查实际下载进度，便在构建运行 309 秒时主动终止。make 最终退出 2，构建退出 130。

**五分钟限制没有依据，是执行者的判断失误。日志不刷新不等于下载停止。** 此次没有等到原 Makefile 的 900 秒超时，不能据此判定 A11 构建失败。原始 [命令日志](evidence/submission-20261021/peer-a11/logs/command.log)、[构建日志](evidence/submission-20261021/peer-a11/run/build.log) 与 [终止记录](evidence/submission-20261021/peer-a11/logs/interruption.json) 保留，不改写为正常结束。

### 第二次：原配置，保留 Makefile 自带超时

重新执行 `make all </dev/null`，没有额外设置短时上限，也没有人为中断，保留 Makefile 原有 `timeout 900 docker compose build`。该次从 12:11:33Z 运行到 12:26:33Z，原 Makefile 的构建超时自然触发，构建退出 124，make all 退出 2，未再人为中断。超时时仍在下载 Debian Packages 索引，后续 test/smoke/镜像扫描未执行。因此只能登记“原配置在本机网络条件下未能在自身时限内完成”。[完整命令日志](evidence/submission-20261021/peer-a11/original-rerun/logs/command.log)、[环境与构建证据](evidence/submission-20261021/peer-a11/original-rerun/run/) 已保留。

### 第三次：仅换下载源的独立诊断，通过

原流程继续运行时，用仓库外的 Dockerfile 和 Compose 覆盖文件另行诊断。改变 Debian 下载源为华为 HTTPS，并通过既有 PIP_INDEX_URL 参数切换 Python 下载源；保留同一基础镜像 digest、Python 依赖锁和哈希校验、Debian 签名校验、服务代码和原 Makefile。使用独立镜像 `e4-buildchecker:241276007-a11-diagnostic`，未覆盖原配置镜像。配置与 [Dockerfile 差异](evidence/submission-20261021/peer-a11/mirror-diagnostic/Dockerfile.diff) 已归档。

该次 12:15:39Z 开始、12:16:14Z 结束，完整流程退出 0：doctor、build、**9/9 单测**、smoke PASS（make/app 退出 0、输出 1、config_h_opened=true、7 份 trace）、仓库/历史/镜像扫描 findings=0。见 [结果](evidence/submission-20261021/peer-a11/mirror-diagnostic/result.json)、[完整命令日志](evidence/submission-20261021/peer-a11/mirror-diagnostic/logs/command.log) 和 [运行证据](evidence/submission-20261021/peer-a11/mirror-diagnostic/run/)。

导出的 toolchain.lock SHA256 为 a5459a49cde9e2299c18eff4dbf581d85277df056eebb043a90a81e0c7615214，与 A11 三份 RERUN 文档声明的值一致；由于对方没有附原始文件，这里是与文档声明对照。该结果说明 A11 工程在本机可以运行，但增加了 README 未说明的换源配置，因此不能算原 README 直接复现通过，也不声称镜像位级一致。

## 网络证据与负向扫描

直接检查正在运行的 APT 下载文件发现其持续增长；后续采样保存在 [apt-progress.json](evidence/submission-20261021/peer-a11/network/apt-progress.json)。同机对同一 Debian Packages.xz 文件请求前 1 MiB，官方 HTTP、HTTPS 均约 14–15 KB/s；华为 HTTPS 约 10 MB/s。网络探测自身的 45 秒采样上限仅用于测速，没有终止正式构建。原始 HTTP 状态、字节数、速率和地址见 [network](evidence/submission-20261021/peer-a11/network/)。证据表明下载慢，不能把日志未刷新当作死锁。

另行使用 A11 扫描脚本检查当前工作区及克隆中的全部 Git 历史：findings=0。新的临时假 Key 被检出（findings=1、退出 1），清理暂存和临时文件后 findings=0。这三次独立检查明确标记 image SKIPPED；镜像扫描通过来自第三次完整诊断，不混用扫描范围。日志见 [logs](evidence/submission-20261021/peer-a11/logs/)。

## 可交给 A11 的问题

1. 在 README 中提供经过验证的慢源处理方式。本次换源诊断保持 digest、依赖哈希和签名检查，已提供可复核的配置差异与完整日志。
2. 根目录明确 E4 README 入口；更新 e4/README.md 第 10 节“其他成员结果尚未填写”的旧状态，目前已有三份 RERUN 文档。
3. E4 产物提交 0a8629f 的作者为中文姓名，邮箱含学号；新版 PPT 要求作者使用学号。建议后续提交设置仓库局部身份，本次未代改其历史。
4. e4/work 当前只跟踪三份 Markdown 成员记录，建议按新版 PPT 保留选定的原始日志。生成的 work 目录未被忽略，应区分临时输出与审查后的提交证据。
5. 三份记录引用的被测 SHA 均可从远端按完整 SHA 取回，但未直接包含在普通 main 克隆的历史中，建议保留可发现的标签或分支。98dc35c 与本次所测 main 的运行文件一致；ff52bbe、57bab6d 与 main 在扫描脚本、模块入口和测试文件上存在差异，不能一概解释为仅文档变更，应说明影响或补验。精确文件列表及取回结果见 [源码关联检查](evidence/submission-20261021/peer-a11/member-report-source-check.json)。

上述反馈由胡博交接；本次没有代发组间消息。A11 对 B11 的复现应另回传日期、执行人、B11 完整 SHA、命令与原始日志，不能用本记录替代。
