# DRAFT 文件交接演示

`artifacts/` 是本例的 ARTIFACT_ROOT：

`artifact://b11/job-draft-example/image_ref.json` 映射到 `artifacts/b11/job-draft-example/image_ref.json`。

该目录包含人工构造的镜像引用、迭代记录、验证文件和文本日志，以及手工 Dockerfile 候选。响应在 `draft/examples/`；其中 sha256 由当前文件的真实字节计算。

**目录内没有镜像文件，也没有真实自动迭代结果。** `image_ref.json` 的 `example_only=true`、`availability=NOT_BUILT` 明确禁止将其当作可用镜像。成功响应仅演示协议形状。

真实 WSL 手工构建日志单独位于 `draft/evidence/`。本地读取演示不等于 A11 已读取，未验证跨组共享路径或网络下载。
