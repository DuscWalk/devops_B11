# 孙静怡 E4 独立运行与对照记录

- 姓名 / 学号：孙静怡 / 241250112。
- Git 身份：`241250112 <241250112@smail.nju.edu.cn>`，只设置仓库本地身份。
- 执行日期：2026-10-19（北京时间）；主运行开始于 22:19:41。
- 执行方式：孙静怡授权 Codex 通过本人的 SSH 公钥连接服务器，以共享系统用户 `duscwalk` 执行。本人已授权操作，但尚未登记本人逐项人工审阅或其他成员新增确认。
- 服务器目录：`/home/duscwalk/241250112/draft`，从真实 GitLab 远端新克隆，未复用其他成员工作目录。
- 仓库：`https://git.nju.edu.cn/devops_b11/devops-project-b11.git`。
- 固定源码：`9765d5794fe43a0c5496be969004d3b84d5b740f`。
- 完整成功目录：`work/20261019T141941-822669957Z`，开始时工作区干净，`make all` 退出 0。
- 假 Key 与清理后扫描：目录见 `verification/scan-detected-command.txt` 和 `verification/scan-cleaned-command.txt`，保留两次扫描输出。假 Key 仅临时暂存，已撤回并删除，从未提交。

## 实际结果

| 检查 | 结果与证据 |
| --- | --- |
| doctor | 2 核 / 1.7 GiB / 69.0 GiB 空闲磁盘；`b11-2gb` 配置；problems 为空，保留原教师阈值和资源警告，见 [env](full-run/env.json) |
| 构建与依赖 | 完整构建成功；保留固定镜像摘要、哈希依赖安装记录、实际版本清单，见 [build](full-run/build.log)、[toolchain](full-run/toolchain.lock) |
| 服务测试 | 4/4 通过，见 [test](full-run/test.log) |
| 冒烟 | 构建退出 1，日志含 `make: not found`，passed=true；完整日志与 JSON 中 build_log 一致，见 [smoke](full-run/smoke.json)、[原日志](full-run/smoke-build.log) |
| 密钥扫描 | 原始全流程通过；假 Key 被检出，扫描器返回 1 / make 返回 2；清理后 make scan 返回 0，见 [核验](verification.json) |
| 收尾 | Git 工作区干净，`.env` 未跟踪且权限 600；只归档选定文本证据，不含私钥、真实 Key 或 `.env` |

服务镜像为 `e4-draft:241250112`，ID 见 [image](full-run/image.json)。未发布到镜像仓库。Docker daemon 与组员共享，构建命中既有缓存，镜像创建时间早于本次运行属于缓存复用；本次确实在个人新克隆内执行了完整构建命令、测试及冒烟，并非无缓存构建或另一台服务器复现。

## 与胡博比较

对照来源为 [胡博 10 月 16 日归档](../hu-bo-20261016/README.md)，机器对照见 [comparison.json](comparison.json)。

- 完整源码 SHA 相同。
- `toolchain.lock` 字节完全相同，宿主 Docker / Compose / Buildx / Git / Make / Python 版本一致。
- 两人均为 4 项服务单测通过；smoke 均构建退出 1、缺少 make、passed=true。
- 镜像 ID、运行时间、耗时与空闲磁盘不同，允许这些差异；不宣称镜像字节完全可复现。
- 本次是对已有记录的实际比较，不代表胡博本次另行人工确认，也不代表 A11 已复现。

## 排查记录与本人贡献

本人贡献为独立克隆及学号身份配置、完整流程复现、密钥负向与恢复验证、选定证据归档及同版本结果对照，无服务实现改动。

首次完整运行 `work/20261019T141918-152043349Z` 已输出完成标记，但本机 PowerShell 对 SSH 包装命令中的退出码变量展开错误，导致外层退出码不可信。第二次完整运行明确取得 `make all` 退出 0；随后输出日志的 tail 因 Windows 输入行尾 CR 报错。后续远端脚本入口统一去除 CR，并独立核验了所有结果文件。上述问题属于本地命令包装，不修改服务代码或验收判据；原始两次运行仍保留在服务器。

剩余事项：孙静怡本人阅读本记录和日志；组长接收并汇总；王硕的独立运行、相邻组只按 README 的复现及正式提交仍由实际参与者完成。
