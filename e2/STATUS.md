# E2 完成状态与验证

更新：2026-09-22。三人工作已整合，A11 确认依据见 AGREEMENT，E2 提交材料已齐备。正式入口为 `.venv/bin/python e2/validate.py`，无需 --proposed。

## 已执行验证

| 项目 | 实际结果 |
| --- | --- |
| Schema 与来源快照 | 正式 Draft 2020-12 Schema 有效；13 个历史文件摘要未改变 |
| 四类接口 | 4 请求、1 类 202、4 查询响应、3 个完整失败 Job 通过 |
| 非法样例 | 6/6 被拒绝，含 job_type=ABC、缺 baseline |
| 公共回归 | 20/20，通过类型/状态/必填/基线/文件完整性与读取检查 |
| MDFixer 回归 | 6/6，MD/RD/RESOLVED 过滤、URI、续行累积补丁、拒绝恢复、超时、复杂规则不猜测 |
| DRAFT 样例 | 请求、反例、202、成功/失败 Job、5 文件摘要与来源通过 |
| MDFixer 样例 | REPAIR、完整 Job、MANUAL 混合报告通过 |
| MDFixer 本地执行 | 1 个候选接受；git apply 检查、构建/测试通过；修改 config.h 后实际重编译输出更新；RD 保留 |
| 文件交接 | DRAFT 5 + REPAIR 3 = 8 文件读取与 SHA-256 通过 |

本轮完整输出：[submission-validation-2026-09-22.txt](evidence/submission-validation-2026-09-22.txt)。实际修复结果：[result.json](evidence/mdfixer-2026-09-22/result.json)、[response.json](evidence/mdfixer-2026-09-22/response.json)、同目录补丁/测试日志。数量按层次分开，彼此有重叠。

## 已发现并修复的失败

9 月 21 日的历史扩展检查为 7/8，发现 configuration_id 漏回显，原始失败日志保留。9 月 22 日整合发现 MDFixer 多个模块的换行/反斜杠语法损坏、URI 正则错误、顶层 Job 不完整、diff 行尾错误、未执行的重检计数；均在本次提交修复并覆盖验证。当前正式入口整体退出 0。

DRAFT 原始网络失败与重试成功日志在 draft/evidence/docker-2026-09-21/。孙静怡的手工 Docker 基线记录 31 个测试、99 个断言通过；胡博核对文件摘要，本次未重新构建 Docker。其镜像约 406 MB，只在来源 Docker daemon。

## 环境和复现

本轮 Python 3.10.12、jsonschema 4.25.1，Git/Make/C 编译器，命令以 duscwalk 执行；作者为 duscwalk <241276007@smail.nju.edu.cn>，其他成员历史作者保留。依赖安装见 README。归档包含固定项目的 Git bundle，不需要网络获取演示源码。

## 范围与后续

E2 交的是契约、设计、样例和过程证据。自动 DRAFT 服务、镜像实际交付、复杂 Makefile、MDFixer 容器执行、环境哈希算法落地、异步幂等存储、A11 检测器重检和跨机器全链路仍属 E3。MDFixer 明示 LOCAL_PROTOTYPE、image_used=false、recheck_performed=false，不把本地构建成功解释为检测器重检成功。

A11 确认由胡博提供，无聊天原文，不虚构线下会议或对方执行日志。当前任务已具备 E2 提交条件；后续项有负责人列在 Backlog。
