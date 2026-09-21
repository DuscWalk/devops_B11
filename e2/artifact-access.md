# E2 产物读取提议与本地演示

状态：**本地演示已验证；传输方式与跨组互读待确认（Q02）**。

## 映射

沿用 A11 的目录映射提议：

```text
artifact://b11/job-e2-read-demo/handoff.txt
→ <ARTIFACT_ROOT>/b11/job-e2-read-demo/handoff.txt
```

本地演示的根目录为 `fixtures/e2-handoff/artifacts/`。URI 不含本机绝对路径，接收方在自己的环境选择根目录。根目录里必须实际存在文件；读取器不提供网络下载、同步或服务部署。

## 可执行演示

从仓库根目录运行（读取器仅依赖 Python 3.10+ 标准库）：

```bash
python3 e2/artifact_access.py \
  --root fixtures/e2-handoff/artifacts \
  --metadata fixtures/e2-handoff/artifact.json
```

读取器核对元数据中的基本必填字段，解析实际文件，读取字节并计算 SHA-256。如果元数据带摘要，则必须一致。输出应包含 `bytes_read: 251`、`checksum_verified: true`，摘要为：

```text
2ebb93c99d19cd77da35f5f48f002427e4213af98750de4be0dd567bd790a431
```

单个演示元数据已通过 A11 的 Artifact 定义检查。文件不存在、摘要错误、缺少 media_type、越出根目录等情况会使读取器非零退出；这些是本地命令行为，尚未映射成双方 HTTP 错误码。

## 交换后需要真实记录的步骤

1. 胡博与 A11 确认传输方式、实际位置、摘要规则和保留期限。
2. 将本演示目录交给 A11；由对方在自己的环境运行命令，记录实际输出。
3. A11 交回一个有完整元数据和文件内容的小样本，B11 按相同规则读取。
4. 在 PAIRING.md 记录双方执行者、日期、来源版本、文件摘要和结果。

本轮只完成本机读取。演示中的 LOG 类型和 job-e2-read-demo 是测试标签；没有发生 DRAFT、BuildChecker、EChecker 或 MDFixer 执行。
