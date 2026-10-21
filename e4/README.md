# B11 · E4 可重复工程环境

本次使用教师 B-draft 模板建立服务骨架，保留已有 E2/E3。课件原件和差异见 [docs/e4](../docs/e4/PPT_COMPARISON.md)。华为云代替手册中的阿里云；本组 SSH 别名为 `HuaweiDevOps`（每人的本机配置可不同）。

提交报告与三人证据入口：[SUBMISSION.md](SUBMISSION.md)。当前进度见 [STATUS.md](STATUS.md)。

## 复现提交版

服务器已有 Docker、Compose、Buildx、Git、Make、Python。共享实验工作账号为 `duscwalk`，可由现有 SSH 登录后执行 `sudo -iu duscwalk`（root 登录使用 `runuser -l duscwalk`）。不需要复制任何私钥到服务器。

```sh
mkdir -p ~/<自己的学号>
cd ~/<自己的学号>
git clone https://git.nju.edu.cn/devops_b11/devops-project-b11.git draft
cd draft
# 固定本次提交版；历史成员日志的实际 SHA 另见 STATUS
git checkout e4-b11-submission-20261021
git config --local user.name '<自己的学号>'
git config --local user.email '<自己的学号邮箱>'
make all
```

每名成员（包括胡博）必须在自己的克隆中实际运行。组员依次构建，避免 2 GB 主机同时构建。不要在共享账号设置全局 Git 身份。`.env` 自动生成，权限 600，E4 保持空值，不需要真实 API Key。

`make all` 顺序执行 doctor → build → test → smoke → scan，输出 UTC 时间命名的 `work/` 目录。代码包含 `.NOTPARALLEL`，证据时间含纳秒，避免同秒覆盖。成功后不要把后续独立 scan 的目录误认为完整运行目录。

若通过非交互 SSH 执行时服务器 `/etc/bash.bashrc` 提示 `PS1: unbound variable`，可在该次命令前设置空值：`PS1='' make all`。本次集成日志记录了此用法，未修改服务器全局配置。

## 2 GB 资源配置及来源

胡博于 2026-10-16 转述：助教参考服务器配置为 2 GB。本组 `make all` 显式选择 `E4_PROFILE=b11-2gb`：2 核、最低 1.5 GiB 可见内存、40 GiB 空闲磁盘。标称 2 GB 的实例约有 1.7 GiB 可见内存，1.5 是本组为系统保留内存留出的容差，并非教师原阈值。

原教师 3.5 GiB 阈值完整保留：`make doctor E4_PROFILE=teacher`。`env.json` 同时记录原阈值、本次阈值、来源、真实 MemTotal 和警告。Swap 不计作物理内存；通过 doctor 不等于构建通过，必须跑完整流程。不要在真实业务阶段假定 2 GB 足够。

## 验收

| 文件 | 检查点 |
| --- | --- |
| source-sha.txt / source-status.txt | 完整源码 SHA；开始运行时工作区干净 |
| env.json | problems 为空；本人身份；真实资源和 b11-2gb 差异说明 |
| build.log / image.json / toolchain.lock | 构建成功，固定基础镜像 digest，真实镜像 ID 和工具版本 |
| test.log | 模板 4 项服务单测通过 |
| smoke.json / smoke-build.log | Docker Server 可用；构建退出码非零，关键行含缺少 make；passed 为 true；完整原始构建输出 |
| secret-scan.txt | 已跟踪文件、全部 Git 历史、镜像历史及环境扫描通过 |

冒烟项目故意缺少 make，不要修复 `Dockerfile.broken`。服务默认以 app 用户运行。资源限制只约束服务容器，不能约束经 docker.sock 发起的宿主机构建。本次没有推送服务镜像到 registry；image.json 的 image ID 不是已发布镜像的 RepoDigest。

## 假 Key 检测

只在自己的干净克隆中执行以下步骤；值运行时生成，不提交。真实密钥不得用于实验。

```sh
python3 -c 'from pathlib import Path; Path("e4-scan-probe.txt").write_text("sk-" + "a" * 24 + "\n")'
git add e4-scan-probe.txt
make scan   # 应失败，保存输出及这个扫描目录
# 只撤回本次临时文件
git reset -- e4-scan-probe.txt
rm e4-scan-probe.txt
make scan   # 应通过，另存清理后的证据目录
```

不要提交假 Key，不需要修改原有 Git 历史。完整流程、负向扫描、清理后扫描是三份证据。

## 贡献和复现交接

三位成员的独立运行与扫描证据已收齐，见 [贡献表](CONTRIBUTIONS.md) 和 [对照说明](COMPARISON.md)。后续新增复现按上面步骤固定提交标签并留下本人的证据。镜像 ID、耗时可以不同，工具版本和预期结果应一致。原始 work 忽略；组长审核选定文本证据后放入 e4/evidence，或收集到最终提交附件。每人的真实贡献记入 CONTRIBUTIONS.md。

已根据胡博提供的仓库地址尝试复现 A11，见 [互评记录](PEER_REVIEW_A11.md)。尚未收到 A11 对 B11 的复现反馈；交接时提供本仓库地址、提交标签及 README，请对方记录所测 SHA、命令、结果和问题。E4 不等待 A11 的真实业务检测报告。由组长按补充通知统一提交，未规定固定附件格式或截止时间。

## 模板调整

保留固定基础镜像 digest 和 Python 包哈希；新增显式 2 GB 配置、完整构建输出、源码 SHA 证据、串行执行及每学号的 smoke 镜像标签；旧 Git 历史含非 UTF-8 文本时扫描按替代字符解码，ASCII 密钥模式照常扫描；限制 Docker 构建上下文为 E4 服务和样例，避免带入 E2/E3 工件。

当前完成情况和执行记录见 [STATUS.md](STATUS.md)。

云端实测原 Debian 源下载较慢，本组服务 Dockerfile 改用华为 Debian HTTPS 镜像（保留原 Debian 签名验证），地址和实际软件版本写入 toolchain.lock。基础镜像 digest 与 Python 包哈希不变。
