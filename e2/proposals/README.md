# 待确认的样例修正

状态：**B11 提议，尚未获得 A11 确认**。来源为 A11 `96f35cc175d12f51f3f7f0915ba35a98d303fcb3`、契约版本 `1.1.0`。

[query_incremental_check.json](query_incremental_check.json) 复制自原样例的 `responses.query_incremental_check`，只增加一个字段：

```json
"input": {
  "configuration_id": "cc-MODE0"
}
```

上面是字段定位片段，完整响应见 JSON 文件。字段值取自原始 `requests.INCREMENTAL_CHECK.input.configuration_id`，也与 `baseline.configuration_id` 相同。

理由：`IncrementalCheckInput.required` 已要求该字段；`Job.input` 的说明要求回显原请求，而原查询样例遗漏了它。修正样例沿用来源版本号用于校验，尚未发布新的共享契约版本。

在仓库根目录执行：

```bash
.venv/bin/python e2/validate.py
.venv/bin/python e2/validate.py --proposed
```

第一条如实审阅原件，当前退出 1，分类型输入检查为 7/8；第二条显式选择本提议样例，8/8 通过，并继续执行回归检查与文件读取演示。`--proposed` 的通过仅表示这份修正草案通过本地检查。

待 A11 确认后，将修正同步到双方认可的来源版本、样例和校验器，并更新本仓库版本记录。关联议题：Q01。
