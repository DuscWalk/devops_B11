# DRAFT E3 模块交接

日期：2026-10-10。负责人：孙静怡；本次由 Codex 按用户授权在该工作区执行，Git 身份沿用 hotori。以下是机器执行结果，不代表王硕、胡博或 A11 已人工复核。

## 已完成

| 任务 | 结果 | 证据 |
| --- | --- | --- |
| 接收公共基线 | 合并胡博 d994302，保留两边 ignore 规则 | 合并提交 1e61e6b |
| 公共本地复跑 | 最终 67/67 检查、82 条命令；含 E2、四风格人工参考及 MDFixer 原型 | [local-final](evidence/draft-sjy-20261010-local-final/summary.json) |
| Tiny Greeting Docker | 3/3：缺 make 故障、参考输出 hello E3、断网重建输出一致 | [docker-https](evidence/draft-sjy-20261010-docker-https/summary.json) |
| fzy 固定源码 | git archive 导出 28195b3a709995354b6c33cec9bb7c9f81532eb6，不复制工作区改动 | [源码清单](evidence/draft-sjy-20261010-fzy-pinned/fzy-source.json) |
| fzy 故障与参考修复 | 同一 Ubuntu digest，broken 缺 make 非零退出，安装工具链后成功 | [broken](evidence/draft-sjy-20261010-fzy-pinned/broken-result.json)、[diff](evidence/draft-sjy-20261010-fzy-pinned/reference.diff) |
| fzy 编译与功能 | 断网 clean 重建产生可执行文件；31 测试、99 断言通过；help 退出 0；筛选输出精确为 alpha 换行 | [5/5 汇总](evidence/draft-sjy-20261010-fzy-pinned/summary.json)、[观察](evidence/draft-sjy-20261010-fzy-pinned/observations.json) |
| 证据核验 | 新增 9 次运行的 337 个归档文件摘要一致，输入清单匹配各自记录的 Git 提交 | [审计](evidence/draft-sjy-audit-20261010.json) |

这些数字描述不同检查层次，不相加为独立测试数。失败 summary 的 1/1 或 2/2 表示失败前执行的断言通过，不能替代整体 result/error 判断。

## 镜像与环境

- Tiny Greeting：`b11/e3-tiny-reference:f82c11c26cff`，Debian GCC14.2 / Make4.4.1。见 [镜像信息](evidence/draft-sjy-20261010-docker-https/image-reference.json)、[环境](evidence/draft-sjy-20261010-docker-https/environment.json)。
- fzy：`b11/e3-fzy-reference:b9c6ded64ac2`，ID `sha256:a06c846e6e9465a979682f95ae48af6b1a5d7893c82831f5b8dc398275f2ae22`。见 [镜像信息](evidence/draft-sjy-20261010-fzy-pinned/image-reference.json)、[基础 digest](evidence/draft-sjy-20261010-fzy-pinned/base-image.json)，同目录有工具链日志及 packages.txt。
- 9 月 fzy 镜像本次确认仍在且 ID 与原记录一致；新 E3 运行使用新标签，不覆盖旧证据。
- 本地公共入口使用 WSL Python3.12.3 / jsonschema4.10.3；Docker 入口由 Windows Python3.11 调用 Docker Desktop Linux daemon。代理仅设置在子进程，没有更改全局配置。
- 镜像仅本机可用，未发布/交付 A11。主机、Tiny Greeting、fzy 环境不同，不混用指纹。基础 digest 在 fzy 同次对照中固定，APT 包版本未全部锁定，记录本轮实际版本。
- 31 个 fzy 测试不包含需要 Ruby 的 acceptance 目标，手工参考构建不代表自动 DRAFT 已实现。

## 真实失败和处理

所有下列目录前缀均为 `e3/evidence/draft-sjy-20261010-`，原始记录不覆盖。

| 后缀 | 实际观察 |
| --- | --- |
| docker | WSL 到 Docker Hub token 网络超时，不计为工具链故障 |
| docker-proxy | 代理重试观察到 make: not found，但 BuildKit 缓存未产生可 inspect 的基础镜像标签 |
| docker-final / docker-retry | 显式 pull 基础镜像后，APT HTTP 下载仍有 502 |
| fzy | broken 预期失败；reference 遭遇 APT HTTP 下载失败，因此整体失败 |
| docker-https / fzy-pinned | 改官方软件源为 HTTPS，Ubuntu 先安装 CA；参考构建和断网验证通过 |

改变的是下载传输方式，不降低判据或绕过证书校验。所有失败均有命令、退出码和日志；人工预期见 fixture README/oracle，实际结果见 observations/logs。

## 公共脚本修正与验证

1. Windows 超时调用 os.killpg 会报 AttributeError，原 timeout 回归实际复现。改为终止本次进程树、收集输出并记录 124 后通过。
2. source_snapshot 遗漏 draft/，新增测试先得到 KeyError；加入目录后通过，runner 的实际字节可追溯。
3. fzy 两个候选通过 BASE_IMAGE 接收同一 RepoDigest，后续容器使用 immutable image ID。
4. Tiny Greeting 参考 Dockerfile 使用同一官方软件源的 HTTPS；这项公共 fixture 修改交胡博一并审阅。

证据基础设施回归在 Windows/WSL 各 6/6 通过；local-final 保存了 WSL 六项回归日志。静态独立复核已完成，不等同于组员人工审核。非阻塞限制：若 Windows taskkill 自身超过 15 秒，日志兜底仍可强化，本轮未出现。

## 复跑

Linux/WSL，仓库根目录，Python3.10+ 与 e2/requirements.txt，每次使用新目录：

```bash
python3 e3/scripts/run_baseline.py --export-evidence e3/evidence/draft-你的新编号-local
docker pull python:3.13-slim
python3 e3/scripts/verify_docker.py --export-evidence e3/evidence/draft-你的新编号-tiny
docker pull ubuntu:24.04
python3 draft/e3-fzy/run.py --source workspaces/draft-fzy --export-evidence e3/evidence/draft-你的新编号-fzy
```

fzy 克隆准备、源码与输出依据见 [README](../draft/e3-fzy/README.md)。本机 WSL 无法访问 Windows localhost 代理，Docker 入口实际使用 Windows Python3.11，并给其进程设置现有 HTTP_PROXY/HTTPS_PROXY。请按机器选择有效代理，不照搬网络配置。

## 交回内容与仍待处理

- 本分支、新证据、broken/reference Dockerfile、复现入口及修正说明已可供审阅。准备提交 fb97e9c、脚本与固定输入修复 7acb523、HTTPS 调整 a5d93f9；最终归档提交由 Git 查阅。
- 孙静怡：DR-01/DR-02 本地执行材料已齐，请本人审阅人工预期与日志后交回。
- 王硕：仍需本人检查四风格参考、原型支持范围和其模块记录。本轮公共验收通过不登记为王硕已执行或审核。
- RV-01 组员人工交叉复核、胡博接收并更新公共 STATUS/Backlog、全组 E3 汇总仍待完成。本轮不替其他成员宣布验收完成。
- A11 实际接收、真实检测器重检、自动 DRAFT 属后续阶段，未执行，也不是本次 E3 交接前置条件。
