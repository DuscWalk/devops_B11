# E2 契约审阅结项

审阅负责人胡博；结项日期 2026-09-22。成员回复与确认依据见 [AGREEMENT.md](AGREEMENT.md)、[DRAFT 历史审阅](feedback/draft-2026-09-21.md)。

| 发现 | 本次处理 | 验证 |
| --- | --- | --- |
| 增量查询漏 configuration_id | 补齐请求回显；Schema 按 job_type 自动选择 input 定义 | 缺字段拒绝；合法四类请求/查询通过 |
| 原标准校验只覆盖外壳 | 新根 Schema 指向 CreateJobRequest，各服务 input 用条件约束；Job 同样验证输入 | 20 个公共回归与 6 非法样例 |
| 202 描述与约束不一致 | job_id/job_type/status 必填且 QUEUED；trace_id/execution 可选 | RUNNING 的 202 被拒绝 |
| 失败只是片段 | 3 个失败样例改为完整 Job；失败 output={}，error 必须存在 | 失败携带 findings 被拒绝 |
| 产物缺实际文件 | DRAFT 5 文件已收到；REPAIR 本地运行产出 3 文件 | 8 份文件可读取并核验摘要 |
| fzy 的 src/Makefile 路径不真实 | 正式教学样例使用根目录 Makefile；不声称教学 MD 为真实发现 | 另提供源码 bundle 的人工 MD 小项目 |
| MDFixer 上传代码转义损坏 | 修复 engine/patch/runner 的语法、正则和 diff 行尾 | 模块导入、回归、实际修复演示 |
| MDFixer 顶层公共字段缺失 | 请求含 trace_id/幂等键；CLI 输出完整 Job；校验器使用公共 Schema | REPAIR 请求/响应标准校验 |
| URI 解析允许静默退化 | 正式 CLI 要求 artifact root、repo URI、完整 SHA；验证工作区 HEAD、报告 commit 和 Makefile 位置 | 源码/URI/版本检查、读取回归 |
| 未重检却报告 remaining=0 | 移除伪计数，明确 recheck_performed=false / NOT_RUN | 输出检查；不能把构建通过当成检测器重检 |
| 无实际源码的修复样例 | 提供人工 config.h 缺失声明项目、独立 Git commit/bundle、完整混合报告 | git apply、构建测试、头文件变更后重编译 |

## 接口稳定性

协议版本保持 1.1.0，提交版标识 b11-e2-r1；校验收紧可能拒绝旧宽松样例，不宣称对所有旧报文兼容。具体差异在 CHANGELOG。A11 原始快照保持不变，正式文件与历史文件在路径上区分。

## E3 范围

实际镜像下载/导出、环境哈希算法、异步队列与幂等存储、真实检测器重检、复杂 Makefile 和全链路评估尚未实现，均有负责人和验收条件列在 Backlog。
