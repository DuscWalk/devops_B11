# E4 运行证据 · 241250110（2026-10-21）

- 仓库分支：feat/e4-reproducible-env
- 源码 SHA：4b3fc1a318e1435750482826a140dda56aaa3457
- 学号目录：/root/241250110/draft
- 成功证据目录：work/20261021T104331-409728919Z/

## full-run/（make all 五步证据）
- env.json：problems 为空，git 身份 241250110
- image.json / toolchain.lock：镜像 e4-draft:241250110；docker-cli 28.5.1、python 3.13.14
- test.log：4 passed
- smoke.json：passed: true；docker_server 29.1.3；build_exit_code 1；make_error_line 含 make: not found
- secret-scan.txt：未发现问题

## leak-test/（假密钥验证）
- scan-detected.txt：检出 leak-demo.txt:1 LLM/API Key sk-d***（make 返回 Error 1）
- scan-after-cleanup.txt：清理后复扫通过

## 重跑对照
与 e4/evidence/hu-bo-20261016/full-run/ 对比：toolchain.lock 完全相同、test.log 均 4 passed、smoke.json 结论一致（server 29.1.3 / exit 1 / make: not found / passed true）。镜像 ID 与运行时间差异属手册允许范围。
