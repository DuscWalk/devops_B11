# B11 E4 提交材料说明

更新：2026-10-19。当前包括**公共环境、胡博及孙静怡授权执行的个人运行证据、两份结果对照**。王硕个人记录、成员人工审阅及相邻组 README 复现仍待补齐，不能登记全组已正式提交。

## 已备材料

- 小组仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11
- 实测源码 SHA：`9765d5794fe43a0c5496be969004d3b84d5b740f`。
- 公共工程：根目录 Makefile、compose.yaml、requirements-dev.lock、services/draft、scripts、fixtures/draft。
- 验收与差异：[STATUS](STATUS.md)、[PPT 对比](../docs/e4/PPT_COMPARISON.md)。
- 胡博原始证据：[evidence/hu-bo-20261016](evidence/hu-bo-20261016/README.md)，包含完整流程、非 root Docker 访问、假 Key 检测和清理记录及逐文件摘要。
- 孙静怡原始证据及对照：[evidence/sun-jingyi-20261019](evidence/sun-jingyi-20261019/README.md)，同一 SHA、新个人克隆、完整流程及两次扫描；工具清单字节一致、测试与冒烟结论一致。
- 每位成员贡献：[CONTRIBUTIONS](CONTRIBUTIONS.md)；其他成员填写 [MEMBER_RUN_TEMPLATE](MEMBER_RUN_TEMPLATE.md)。
- 操作和交接：[README](README.md)、[HANDOFF](HANDOFF.md)。
- 课件、教师实验包原件及摘要：docs/e4/。

## 胡博完成部分可用说明

本组在已有 E2/E3 仓库上接入教师 B-draft 服务骨架。按助教参考 2 GB 配置，在华为云 Ubuntu 22.04（2 核、实际可见内存 1.7 GiB、无 swap）完成 make all：镜像成功构建，4 项服务单测通过；冒烟样例因缺少 make 按预期失败，完整日志与退出码保存，passed=true；仓库、全部 Git 历史和镜像密钥扫描通过，另验证了假 Key 能被检出、清理后扫描通过。

原包要求 3.5 GiB，本组以显式 b11-2gb 配置适配助教参考规格，env.json 同时记录原阈值、采用阈值和真实资源。原默认 teacher 配置仍会拒绝该主机，相关证据附上。基础镜像 digest、Python 依赖哈希不变；为解决下载停滞改用华为 Debian HTTPS 源，保留签名验证并导出实际版本。补全 smoke 完整日志、修复历史非 UTF-8 解码、避免并行步骤和证据覆盖。E3 本地 67 项基线回归仍全部通过。

胡博授权 Codex 执行上述准备、修复、云端运行和整理，E4 新提交作者经本人确认使用学号 241276007。现有成员历史成果不改作者。其他组员独立执行与组间复现未代做、未填为通过。

## 最终提交前补齐

1. 王硕在自己学号目录运行同一 SHA，交回成功日志、负向扫描日志和真实贡献说明；孙静怡运行材料已齐，待本人审阅及组长接收。
2. 审阅已归档的孙静怡/胡博 toolchain/test/smoke 对照；镜像 ID 不同、工具版本与结论一致。该对照不等于双方新增人工确认。
3. 留下相邻组仅按 README 重跑的实际反馈。
4. 由胡博汇总，按课程平台要求统一提交；补充通知未规定固定文件格式或截止时间。

提交附件不含 .env、SSH 私钥、缓存或临时假 Key。服务镜像保留在 HuaweiDevOps 的 Docker daemon，名称 e4-draft:241276007；没有向外部 registry 发布，不虚构可拉取的镜像地址。
