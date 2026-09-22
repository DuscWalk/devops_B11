# LMS 提交说明

本材料对应 E2“需求与接口契约”。课件第 15 页要求接口、设计、贡献与完成情况；LMS 具体附件格式以作业页面为准。

## 可填写内容

```text
实验：E2 需求与接口契约
小组：B11；配对组：A11
成员：孙静怡（DRAFT）、王硕（MDFixer）、胡博（接口与联调）
仓库：https://git.nju.edu.cn/devops_b11/devops-project-b11
发布标记：e2-b11-submission-20260922
材料入口：e2/README.md
验证命令：python e2/validate.py（按 README 安装依赖）
结果：四类契约/反例、20+6 个回归、8 个产物读取、MDFixer 本地补丁构建验证通过
边界：E2 无需部署 API；真实镜像传输、检测器重检和四服务端到端在 E3 继续
```

固定版本入口：[发布标记下的材料](https://git.nju.edu.cn/devops_b11/devops-project-b11/-/blob/e2-b11-submission-20260922/e2/README.md)。通过仓库提交页或 `git rev-parse e2-b11-submission-20260922^{commit}` 取得完整提交 SHA，一并填写 LMS。外部提交包附有已填写完整 SHA 的 LMS 文本，不在 Git 文件中伪造自身提交哈希。

## 材料清单

| 类别 | 入口 |
| --- | --- |
| 小组/成员/贡献 | README、CONTRIBUTIONS.md、Git 历史 |
| 统一模型、四类交接、错误 | task.schema.json、contract-examples.json、openapi.yaml、两模块 examples |
| 产物及读取 | artifact-access.md、fixtures/、真实修复 evidence |
| 设计和确认 | Backlog、ADR、AGREEMENT、PAIRING、CONTRACT_REVIEW |
| AI 和变更 | AI_USAGE、CHANGELOG |
| 验证/失败/后续 | validate.py、STATUS、evidence |

## ZIP 内容与复现

提交 ZIP 由固定 Git 提交导出，包含代码、上述全部文档、小型产物、执行记录和 MDFixer project.bundle；不包含 `.git`、虚拟环境、密钥、大型镜像、临时工作区。Git 历史通过仓库和成员 SHA 追溯。

解压后按 README 建立 Python 环境，运行统一入口。Git/Make/C 编译器为演示前置条件；不需要 Docker、不需下载 fzy 源码就能跑 E2 校验。孙静怡的实际镜像构建如需另行复现，按 draft/PROJECT.md 运行，可能需要网络及 Docker。

LMS 如只允许链接，使用仓库、固定提交 SHA 和材料入口；如要求附件，可上传 ZIP 及配套 LMS 文本。确认授课教师/助教对仓库有读取权限。本次未代登录或提交 LMS。
