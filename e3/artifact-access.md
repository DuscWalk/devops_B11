# E3 产物读取与交接

沿用 E2 已确认的 `artifact://<group>/<job_id>/<name>` → `$ARTIFACT_ROOT/<group>/<job_id>/<name>`。代码复用 `e2/artifact_access.py`，公共 Schema 不变。

统一入口将本次 MDFixer 原型产物复制到独立消费方根目录再读取，记录 `artifact-receipt.json`，并篡改一个文件验证摘要拒绝，然后恢复。它证明 B11 本地两个目录之间可读取，`a11_received=false`；不能作为 A11 收件证明。

## 接收方检查清单

1. 收到文件目录或归档，记录发送版本、生产任务、源码完整 SHA 和配置。
2. 解压到自己的独立 `ARTIFACT_ROOT`，不得只共享 URI 字符串。
3. 从 Job 的 `output.artifacts` 逐项取 URI、媒体类型和 SHA-256；用读取器定位并核验。
4. 对照源码 commit、Makefile 路径与 report.commit，再运行构建/验证。
5. 留存接收命令、退出码、日志和摘要；然后才能登记“实际互读完成”。

IMAGE JSON 不是镜像本体。后续若用 `docker save/load`，需另附镜像归档 SHA-256、实际 image ID、OS/架构和构建/验证命令；若用 registry，提供接收方真正可拉取的 digest。E3 不要求立即发布注册表或传输大型镜像，组员交接只传小型源码和证据。

产物元数据必须完整；有 sha256 就必须核验，缺文件、路径越界和摘要不符都拒绝。日志和证据保留原始内容，修订以新目录追加；清理镜像或跨组共享文件前协调。
