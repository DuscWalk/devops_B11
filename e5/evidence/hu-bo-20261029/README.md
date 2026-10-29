# 胡博 E5–E7 云端实验证据

- 执行人：胡博，241276007；系统用户 duscwalk
- 服务器：学院分配的 Huawei Cloud ECS；2 CPU、约 1.7 GiB 可见内存、无 swap
- 实验目录：/home/duscwalk/241276007/e5-b11-20261029
- 云端实验代码初始提交：1075c1e8c887a9816026184342f93cbd17232311
- 实验：B11 / B-DRAFT，课程微型 hello E3 样例

## E5–E7 结果

初始 Docker build 在 RUN make 处得到 make not found，Docker build 退出 1；lab_cloud.py 将预期失败归档后退出 0，并生成 error-driven 与 context-driven 两类提示。

Codex 对两类提示各生成一个候选，版本信息限制、SHA 和选择理由见仓库的 e5/labs/B-draft/work/candidate/provenance.json。选择的 context-driven 候选使用固定基础镜像 digest，安装 build-essential，并根据已测网络情况切换到华为 Debian HTTPS 镜像。候选构建退出 0，随后用生成镜像的同一完整 ID 以 --network none 运行，退出 0，stdout 为 hello E3。

基础环境 doctor 报告通用最低 4 GiB 内存未满足；学院分配的 2 GB 服务器上 E5、E6、E7 均实际完成。结论不外推到论文数据集或更大项目。

E6 自动构建与证据校验通过；E7 的 25 项单测和五个真实场景均通过。完整运行记录分别在 `e6-hubo-20261029-mirror/` 与 `e7-hubo-20261029-customtest/`。E7 另外包含 B11 自定义多阶段候选拒绝测试。

服务镜像通过单独的 `service-base-mirror.Dockerfile` 适配层切换 Debian HTTPS 和 PyPI 镜像，课程原 Dockerfile 与依赖锁未修改。`build-hubo-20261029/` 保留官方源诊断和适配构建日志；其中 `service-build-official-network.log` 与 `e7-hubo-20261029-mirror/` 是网络诊断尝试，不计入通过结果。最终实验命令均以远端 `duscwalk` 用户执行。

## 文件

- e5-02/iter-01/：失败基线、Dockerfile、Make 数据、原始构建日志、错误定位 JSON、两种提示
- work/e5-02/：候选构建日志、image inspect、image ID、断网运行 stdout/stderr 和退出码
- controller/：外层命令、退出码、起止时间、云端代码 SHA 和运行前后 Git 状态
- doctor.txt：课程包环境检查原始输出
- secret-scan.txt：仓库工作区和 Git 历史的扫描结果
- build-hubo-20261029-customtest/image-secret-scan.txt：最终服务镜像的历史和环境变量扫描
- e6-hubo-20261029-mirror/：E6 双轮构建、镜像运行、输入哈希和 JSON 结果
- e7-hubo-20261029-customtest/：最终 E7 五场景、服务单测和 CSV/JSON 汇总
- build-hubo-20261029/：服务镜像官方源诊断、镜像源构建、inspect 和单测
- build-hubo-20261029-customtest/：含 B11 自定义测试的最终镜像构建和 25/25 单测
- ci/：组级 GitHub Actions 正常、失败和恢复运行 artifacts；main 保护配置、失败 PR 合并拒绝输出及 PR 合并记录

摘要：同目录 checksums.json。课程代码来源和包清单：docs/e5/README.md、docs/e5/Student_Cloud_MANIFEST.sha256.json。
