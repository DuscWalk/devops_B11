# AI使用记录

工具/模型/日期：Trae 内置模型（DeepSeek-V4-Pro）/ 2026-11-18
输入上下文与问题：E8/E9 B组逐步实操手册、公共准备与提交排错手册；问题为按手册逐步执行实验、编写个人测试与报告。
模型建议：按手册顺序生成执行脚本（e8_steps.sh/e9_steps.sh）与报告草稿；自主任务选取手册示例2B（E8配方行保持）与2D（E9变量风格）并补充断言。
采纳/拒绝及理由：采纳手册规定的步骤与示例测试；在2D示例基础上自行增加mixed风格独立用例（test_mixed_style_patch_keeps_header_macro），并在2B示例中增加plan长度断言，作为自己的输入变化；拒绝修改lab.py实现，保持参考代码边界。
人工修改：逐项核对每步输出与手册预期一致；报告中SHA、镜像ID、gcc/make版本均取自实际运行输出；AI草稿中的占位值全部替换为真实证据值。
实际验证命令/输入/结果：bash e8_steps.sh（8步STEP_EXIT_CODE=0）、bash e9_steps.sh（6步STEP_EXIT_CODE=0）；docker run python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v，Ran 10 tests OK；镜像构建日志work/environment-build-20261118.log（成功）。
未调用模型时写明未调用；记录参考实现和自己的贡献边界：labs/e8e10/lab.py、run_lab.py、classroom_helpers.sh为课程参考代码，未改动；本人贡献为test_profile.py新增StudentE8B与StudentE9B两个测试类（共3项测试）以及个人报告/ADR/本AI使用记录三份文档。
