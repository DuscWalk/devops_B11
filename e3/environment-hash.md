# 构建环境指纹提案 v1

状态：`PROPOSED_B11_ONLY`。胡博已提供可执行方案和实际本地指纹；A11 未确认，没有改 E2 公共协议或把提案值写回其 baseline。

## 生成与复算

```bash
.venv/bin/python e3/scripts/environment.py
.venv/bin/python e3/scripts/environment.py --output /tmp/一个未存在的文件.json
```

摘要为 `SHA-256(UTF-8(JSON(identity)))`：键排序 `sort_keys=True`，紧凑分隔符 `(',', ':')`，`ensure_ascii=False`，无末尾换行。实现是 `common.canonical_bytes` / `common.fingerprint`。只对 `identity` 求摘要，运行时间、路径、任务 ID 和证据目录不参与。

| 执行方式 | identity 字段 |
| --- | --- |
| LOCAL_HOST | 规范版本、OS、架构、发行版、内核、实际 cc/GNU Make 版本、编译器 target、CFLAGS、逻辑工作目录 |
| DOCKER | 规范版本、实际镜像 ID、OS/架构、容器 cc/Make 版本、包清单摘要、CFLAGS、容器工作目录 |

配置名分别为 `b11-e3-tiny-local-v1`、`b11-e3-tiny-container-v1`。不能冒用 E2 的 `fzy-default-gcc13-make4.3`。镜像 tag 只是名称，实际运行优先按 immutable image ID 对照。

## 适用范围和待确认事项

本地指纹没有完整宿主库/包清单，不能保证环境完全相同；用于本次微型案例的比较和审计。后续真实检测优先以不可变容器镜像加显式构建配置统一环境。

提交版本和输入源码摘要另由 `source.json` 追溯，不混入环境指纹；命令及配置需要同时匹配。A11/B11 待共同确认：字段规范、环境与 configuration_id 的映射、C0/C1 环境一致性检查、配置或镜像变更如何重建 baseline。未确认前不将此提案当作双方正式哈希算法。
