# MDFixer 固定人工项目

来源：B11 成员在 2026-09-22 整合原型时编写的教学项目，detector=MANUAL。它不是 fzy、A11 实际检测结果或论文数据集。源文件、报告、Git bundle 与摘要均在本目录。

固定独立源码提交：`a6d77c66a910b3dbfbf5444cf7b86cc893cf0c69`。该 SHA 属于随附 project.bundle 的仓库，不是 B11 主仓提交；source.json 明确其来源和逐文件摘要。报告中的 repository.url 指向保存 bundle 的 B11 仓库，源码由 bundle 取得。

故障：app.c 包含 config.h，但 Makefile 第 9 行 app.o 的 prerequisites 缺 config.h。构建初始可成功，修改头文件后可能漏重编译。legacy.h 被声明但未包含，作为不自动删除的 REDUNDANT 样例。

报告为独立 ErrorReport 对象，schema_version/repository/findings，位置为 Makefile:9；evidence.actual_read 是依据源码 include 人工标注，不声称进行了动态追踪。

执行 `.venv/bin/python mdfixer/demo.py`：克隆 bundle、核对 commit、只生成 MISSING 补丁、恢复工作区、验证 patch 可应用、构建/测试以及头文件变化重编译。实际输出见 e2/evidence/mdfixer-2026-09-22/，检测器重检 NOT_RUN。
