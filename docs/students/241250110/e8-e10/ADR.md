# 决策记录

背景与约束：E8/E9 B轨道与A组接口解耦，使用scan()生成的固定报告作为输入；候选补丁不得直接写回源项目，先经git apply --check核对；每个样例project内部有独立Git提交身份（C0），外层仓库另保存学生源码SHA，两者用途不同。

选择与替代方案：
- B（共享变量怎样处理）：macro风格下patch选择修改DEPS变量定义而非目标行；与direct（目标行追加）、mixed（保留宏引用、目标行追加）构成三种策略。代价：共享变量被其他目标引用时可能扩大作用范围，当前教学配置仅覆盖单一引用目标，跨目标影响留待扩展分析（E9结论.txt已记录）。
- 身份绑定：报告commit必须等于样例HEAD，否则抛出ValueError('STALE_REPORT')直接拒绝，避免用其他提交的发现改当前文件。
- B（失败怎样保证原目录不变）：拒绝路径（STALE_REPORT/UNSAFE_PATH/UNSUPPORTED_*）均不修改源Makefile，以字节比对（SOURCE_BYTES_UNCHANGED）确认。

代价与覆盖范围：仅支持main.o/helper.o两个显式目标、变量展开上限8层、CFLAGS仅-O0/-O1/-O0 -DMODE=1；不覆盖隐式规则、多目标共享变量与复杂Make语法。

验证命令与实际证据：e8_steps.sh（8步）与e9_steps.sh（6步）逐步执行，各步STEP_EXIT_CODE=0；单元测试Ran 10 tests OK（日志work/unit-tests-20261118.log）；证据目录work/e8-B-manual.h5ydgq与work/e9-B-manual.NVbSf2。
