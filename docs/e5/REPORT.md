# E5–E7 实验报告：论文 1 复现（B11 / DRAFT）

日期：2026-10-29。执行人：胡博，241276007。轨道：B / DRAFT。服务器：学院分配的 Huawei Cloud ECS，2 CPU、约 1.7 GiB 可见内存、无 swap。SSH alias `HuaweiDevOps` 默认以 root 登录；所有实验命令均通过 `sudo -u duscwalk` 执行。云端实验仓库：`/home/duscwalk/241276007/e5-b11-20261029`。

## 实验结果

|检查项|结果|证据|
|---|---|---|
|环境检查|Docker 29.1.3、Compose 2.40.3、Buildx 0.30.1 可用。课程 doctor 的通用 4 GiB 检查未通过；学院提供的 2 GB 配置仍完成 E5、E6、E7。|[doctor 输出](../../e5/evidence/hu-bo-20261029/doctor.txt)|
|E5 失败基线|Docker build 到 `RUN make`，实际出现 `make: not found`，构建退出 1；课程脚本将预期失败归档并生成两类提示。|[失败日志与结果](../../e5/evidence/hu-bo-20261029/e5-02/iter-01/)|
|候选构建与运行|选择 context-driven 候选，固定 base digest，安装 `build-essential`，使用华为 Debian HTTPS 镜像。构建退出 0；同一完整 image ID 在 `--network none` 下退出 0，输出 `hello E3`。|[候选](../../e5/labs/B-draft/work/candidate/Dockerfile)、[镜像和运行证据](../../e5/evidence/hu-bo-20261029/work/e5-02/)|
|E6 自动构建|通过。第一轮分类为 `MISSING_MAKE`；候选第二轮构建退出 0，运行同一镜像 ID 成功，输出匹配。证据校验器返回 `passed: true`。|[E6 报告和日志](../../e5/evidence/hu-bo-20261029/e6-hubo-20261029-mirror/evidence/)、[校验器输出](../../e5/evidence/hu-bo-20261029/e6-hubo-20261029-mirror/runner/)|
|E7 门禁|通过。25 项服务单测和正常、输出不符、无效候选、构建失败、运行超时五个真实场景全部通过；超时容器已清理。|[gate-result.json](../../e5/evidence/hu-bo-20261029/e7-hubo-20261029-customtest/gate/gate-result.json)、[results.csv](../../e5/evidence/hu-bo-20261029/e7-hubo-20261029-customtest/gate/results.csv)|
|B11 自定义测试|通过。新增测试拒绝带第二个构建阶段的候选 Dockerfile；该测试包含在 25/25 服务单测中。|[自定义测试](../../e5/labs/B-draft/services/draft/tests/b11_custom/test_candidate_policy.py)、[单测日志](../../e5/evidence/hu-bo-20261029/build-hubo-20261029-customtest/unit-tests.log)|
|密钥扫描|通过。工作区和 Git 历史扫描 1576 个文件，最终服务镜像扫描 33 个文件/镜像元数据；均未发现问题。|[工作区与历史](../../e5/evidence/hu-bo-20261029/secret-scan.txt)、[镜像扫描](../../e5/evidence/hu-bo-20261029/build-hubo-20261029-customtest/image-secret-scan.txt)|
|GitHub CI 与合并门禁|PENDING。当前环境的 GitHub CLI 未登录，无法创建课程要求的组级 GitHub 仓库、配置 main 保护、运行失败 PR 和修复合并演示。|课程学生包 `docs/04_GitHub_CI与合并门禁.md`；尚无 GitHub run/artifact 链接|

## 来源与方法

B-DRAFT 参考代码来自课程包 `DevOps_1020_Student_Cloud.zip`，其中 77 项 SHA-256 校验通过。云端初始代码提交为 `1075c1e8c887a9816026184342f93cbd17232311`；Git 作者按要求设置为 `241276007 <241276007@smail.nju.edu.cn>`。本组自定义测试放在 `services/draft/tests/b11_custom/`，与课程包原始文件分开。

失败基线使用固定的 Python 3.13 slim digest `sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f`。E5 两类提示基于真实失败日志生成。OpenAI Codex 按两类提示各生成一个 Dockerfile；实际服务端模型版本不可见，本次没有调用外部模型 API。候选完整文本、回复、哈希、选择理由和修改记录见 `e5/labs/B-draft/work/candidate/provenance.json`。

## 资源与网络诊断

课程 doctor 检查通用最低 4 GiB，学院服务器可见约 1.7 GiB，因此 doctor 返回 1；按课程服务器规格继续实测。本次服务构建、E6 和 E7 均成功，E7 期间仍约有 1 GiB 可用内存。结论限于本次微型样例和测试，不外推到论文数据集或更大项目。

构建没有被任意的 5 分钟上限截断。课程服务构建采用指南给出的 1200 秒预算，E5/E6/E7 采用指南给出的 600 秒构建预算。诊断发现主要阻塞来自镜像源：官方 Debian HTTP 源在服务构建中超过 4 分钟仍未完成 9.6 MB 索引下载；改走华为 HTTPS 后，同一构建下载 10.2 MB 索引用时 1 秒、25.3 MB 软件包用时不足 1 秒。PyPI 官方源下载 1.3 MB 的 Pygments 包约 1 分 51 秒，速率 11.7 kB/s；华为 PyPI 镜像下载同一包速率约 92.1 MB/s。原始课程 Dockerfile 未修改；服务镜像通过单独的 [镜像源适配层](../../e5/evidence/hu-bo-20261029/service-base-mirror.Dockerfile) 构建，Python 依赖仍按课程锁文件的哈希安装。E7 最初尝试的预置候选使用官方 Debian 源，部分构建日志仅作为网络诊断归档，不计入通过结果；最终五场景使用本组已验证的候选。

## 证据索引

本报告内路径均相对仓库根目录。完整运行记录在 `e5/evidence/hu-bo-20261029/`，包含输入副本、Dockerfile、image inspect、stdout/stderr、退出码、JSON 报告和 SHA-256 清单。E5、E6、E7 都仅验证课程包内的 `hello E3` 微型样例；没有运行论文数据集实验。
