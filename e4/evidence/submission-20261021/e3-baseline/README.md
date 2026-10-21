# 整合期间的 E3 本地回归

2026-10-21 执行 `.venv/bin/python e3/scripts/run_baseline.py`，67/67 检查通过，记录 82 条命令。
本目录选择保存原始 summary、source、environment、commands、observations、artifact-receipt 和完整命令日志。原始运行目录为 e3/work/20261021T115012Z-df3f693b，临时构建目录和二进制不提交。

被测源码提交及当时状态以 source.json 为准：06d94d976f921a4d4cd1b4178fd9980f27a87926，当时新增的 E4 汇总文件尚未跟踪，E3 运行输入未改动。后续只整合 E4 说明和证据，既有 E2/E3 源码与实验材料保持原内容。此命令包含 E2 校验与 E3 证据回归，不执行 E3 Docker 验收或 A11 业务检测器。
