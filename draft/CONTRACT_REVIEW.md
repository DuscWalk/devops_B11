# DRAFT 对 Q03 / Q07 的回复草稿

依据：胡博分支 `docs/e2-contract-alignment` 的固定提交 `e8bf6eee0acf00f86ba028ecf3c19399811992cd`，以及其中保存的 A11 1.1.0 来源快照。本文件供组内审阅，尚未发送给 A11，不代表双方已确认。

## Q03：输入与环境交接

保留 `POST /v1/dockerfile-jobs`、DRAFT Job 和现有请求字段。`repository`、`build.command`、`verify_command` 必填。当前样本显式填写 `max_iterations=5`、`timeout_seconds=1800`，建议它们也是服务默认值，但默认行为尚需确认。

工作目录建议默认为仓库根目录；当前严格输入 Schema 不接受新增 `project_root`，因此不直接加字段。若 A11 需要子目录构建，由胡博组织变更输入 Schema。本次 fzy 根目录 Makefile 已核实。

将验证命令由原样例的 `make && ./fzy --help` 加强为 `make check && ./fzy --help`；实测可用。单次构建成功与验证成功均应满足后，才可将自动任务标为 SUCCEEDED。

### IMAGE 文件如何交给下游

`fixtures/draft-handoff/artifacts/b11/job-draft-example/image_ref.json` 给出提议内容：

- `image`：下游 `input.image` 的候选值。示例 tag 仅为演示，尚无镜像可拉取。
- `repository`：源码仓库与完整 commit。
- `project_root`：容器内源码路径，可用于 FULL_CHECK 的 `project_root`。
- `configuration_id`、`clean_build_command`：传给检测请求的候选配置。
- `distribution`：建议支持 registry 或 docker-save，由双方选择。跨 Docker daemon 不能仅凭本地 tag 使用镜像。
- `image_id`、`repo_digest`：当前为 null，真实构建/发布后填写。镜像配置 ID、注册表 manifest digest 和 tar 文件摘要是不同概念。

消费者先读取 IMAGE 产物文件，确认它不是 `example_only`，实际取得镜像并核验标识后，才映射这些字段。不得只把 JSON 中的 tag 复制到 A11 就宣称交付完成。

### 日志与验证结果

成功查询样例增加两个 LOG 引用，分别指向 JSON 格式的每轮命令、退出码、修改、选择理由和文本日志；同时给出 TEST_RESULT 文件。所有演示产物含真实文件摘要，但内容是人工编写的演示，不是自动执行证据。产物类型沿用参考枚举，文件内部格式是待确认提议。

失败样例使用完整 Job、`status=FAILED`、空 `output` 与 `ENV_3002`，对齐胡博 Q05 的建议。具体迭代日志保留/访问策略还需胡博和 A11 统一；当前不擅自修改公共失败响应约束。

## Q07：构建配置与环境标识

本机实测 GCC 13.3.0 / Make 4.3，不能宣称已经生成 A11 示例的 Ubuntu22.04/GCC10 环境。建议配置名 `fzy-default-gcc13-make4.3`；其编译选项为该固定提交的 Makefile 默认设置。A11 若依赖另一版本工具链，需在镜像定稿前反馈。

建议 DRAFT 负责提供真实镜像标识、平台、工具版本、构建配置和命令；胡博与 A11 共同确定 `build_environment_hash` 的规范化字段、序列化方式及算法，并明确 baseline 中存储什么以供对比。源码 commit 单独追溯，不应简单把变化的 C0/C1 commit 混入“同一环境”哈希。当前镜像尚未生成，环境哈希保持 null，不用任意示例字符串假装计算完成。

## 需胡博汇总确认

1. A11 接受 Ubuntu24.04/GCC13 候选，还是需要 GCC10？
2. 仓库根目录、5 次迭代/1800 秒默认值与加强后的验证命令是否接受？
3. IMAGE、迭代记录和验证文件内部格式是否足够，镜像采用哪种交付方式？
4. configuration_id 的所有者、环境哈希规范和基线比较依据是什么？

上述问题保留待确认；不改动胡博分支中的公共文件和协商状态。

## 2026-09-21 Docker 验证补充

本文件前面的 image_ref 描述针对人工契约样例，该样例保持 `NOT_BUILT`。现已额外构建真实本地镜像 `b11/fzy:28195b3-baseline`，独立容器断网重建及 31 个测试通过。真实元数据见 `evidence/docker-2026-09-21/image_ref.json`，包含 image ID 和本地可用状态。尚无注册表 digest、对外交付或 A11 确认，环境哈希仍待统一；不能直接把本地镜像名当成 A11 可拉取的地址。
