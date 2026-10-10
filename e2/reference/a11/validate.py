#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2 接口契约校验器（A11 组）

用法：
    python validate.py

校验对象：task.schema.json（契约定义）+ contract-examples.json（样例）

输出分三部分：
  第一部分  契约检查（零依赖）
           四类请求 / 五类响应 / 三条系统错误 / 六类非法样例是否满足契约
  第二部分  负向对照（零依赖）—— 15 项
           程序化篡改【完整合法样例】且只改一处，期望被拒绝。
           用于证明"校验器不会静默失效"：规则写了，就必须真的生效。
  第三部分  jsonschema 标准交叉校验（可选）—— 9 项
           环境中若安装了 jsonschema 库则额外执行；未安装则跳过，不影响结论。

对应课堂验收（PPT Slide 25）：
  检查 01  四类任务的请求/响应/错误/发现/产物样例是否满足契约
  检查 02  job_type 改为 ABC 等未定义值 → 必须被拒绝（第二部分用例 1）
  检查 03  INCREMENTAL_CHECK 删除 baseline → 必须被拒绝（第二部分用例 2）
  检查 04  「检测发现」与「系统执行错误」必须分离表示

本组自加：
  检查 05  delta 与 findings 必须正交，且 delta 不得出现在非增量检测响应中
  检查 06  基线一致性：baseline.commit == base_commit；configuration_id 必须与本次一致

设计取舍：
  1. **零第三方依赖** —— 助教要在任意机器上当场运行，零依赖 = 零安装风险。
  2. **单一来源** —— 四类任务的必填字段与全部枚举【从 task.schema.json 派生】，
     本脚本不重复定义。否则契约改了、校验器没改，就会出现"契约承诺了规则却执行不了"
     的静默漂移（本组曾因此漏掉 configuration_id 一致性，见 CHANGELOG 修正记录）。
  3. 业务规则（跨字段一致性，如 baseline.commit == base_commit）无法由 JSON Schema
     表达，必须由本脚本兜住 —— 这是契约能被真正执行的关键。
  4. 负向对照是【刻意设计的对照实验】：正向校验只能证明"合法的能通过"，
     证明不了"非法的会被拒"。两者缺一不可。

退出码：0 = 全部通过；1 = 存在失败项。
"""
import copy
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE, "task.schema.json")
EXAMPLES_PATH = os.path.join(BASE, "contract-examples.json")

# 契约中的枚举与必填规则【一律在运行时从 task.schema.json 派生】，本脚本不重复定义。
# 这样契约是唯一来源：改 schema 即改行为，不存在两份定义靠人工同步。
SCHEMA_VERSION = "1.1.0"      # 占位，加载 schema 后由 const 值覆盖
JOB_TYPES = ()
STATUSES = ()
ERROR_CODES = ()
ARTIFACT_TYPES = ()

ARTIFACT_URI_RE = None        # 占位，加载 schema 后由 $defs.ArtifactUri.pattern 编译

def input_def_name(job_type):
    """job_type → schema 中对应 input 定义名，按【命名约定】推导。

    FULL_CHECK → FullCheckInput。不硬编码映射表，因此契约新增 job_type 时本脚本无需改动。
    """
    return "".join(w.capitalize() for w in job_type.split("_")) + "Input"


# ================================================================ 契约加载
def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def derive_input_rules(schema):
    """全部 job_type 的必填规则【从 schema 的 JobType 枚举 + $defs 派生】。

    本脚本不重复定义任何字段名规则，也不硬编码 job_type 列表 ——
    契约是唯一来源：改 schema 即改行为，不存在"两份定义靠人工同步"。
    """
    defs = schema["$defs"]
    rules = {}
    for jt in defs["JobType"]["enum"]:
        node = defs.get(input_def_name(jt))
        if node is None:
            continue
        required = list(node.get("required", []))
        nested = {}
        for field in required:
            sub = (node.get("properties") or {}).get(field) or {}
            if "$ref" in sub:
                target = defs[sub["$ref"].rsplit("/", 1)[-1]]
            elif "required" in sub:
                target = sub
            else:
                continue
            if target.get("required"):
                nested[field] = list(target["required"])
        rules[jt] = {"required": required, "nested": nested}
    return rules


SCHEMA = load_schema()
INPUT_RULES = derive_input_rules(SCHEMA)

# —— 从 schema 派生枚举与正则（单一来源，杜绝双份定义）——
_D = SCHEMA["$defs"]
SCHEMA_VERSION = _D["CreateJobRequest"]["properties"]["schema_version"]["const"]
JOB_TYPES = tuple(_D["JobType"]["enum"])
STATUSES = tuple(_D["Status"]["enum"])
ERROR_CODES = tuple(_D["SystemError"]["properties"]["code"]["enum"])
ARTIFACT_TYPES = tuple(_D["Artifact"]["properties"]["type"]["enum"])
ARTIFACT_URI_RE = re.compile(_D["ArtifactUri"]["pattern"])


# ================================================================ 小工具
def is_sha40(v):
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v)


def is_artifact_uri(v):
    """三段式校验：artifact://<group>/<job_id>/<name>（与 ADR-002 一致）。"""
    return isinstance(v, str) and bool(ARTIFACT_URI_RE.match(v))


def _missing_nested(node, fields):
    return [f for f in fields if not isinstance(node, dict) or node.get(f) in (None, "", [], {})]


# ================================================================ 校验：请求
def validate_request(doc, expect_type=None):
    errs = []
    if doc.get("schema_version") != SCHEMA_VERSION:
        errs.append(f"schema_version 必须为 '{SCHEMA_VERSION}'，实际 {doc.get('schema_version')!r}")
    if not doc.get("trace_id"):
        errs.append("trace_id 必填")
    if not doc.get("idempotency_key"):
        errs.append("idempotency_key 必填（客户端用幂等键表达『同一逻辑请求』，不指定 job_id）")
    if "job_id" in doc:
        errs.append("创建请求不得由客户端指定 job_id（job_id 由服务端生成）")

    jt = doc.get("job_type")
    if jt not in JOB_TYPES:
        errs.append(f"job_type 非法：{jt!r}（合法值：{list(JOB_TYPES)}）")
        return errs
    if expect_type and jt != expect_type:
        errs.append(f"样例挂载位置与 job_type 不符：{expect_type} vs {jt}")

    inp = doc.get("input")
    if not isinstance(inp, dict):
        errs.append("input 必须是对象")
        return errs

    rule = INPUT_RULES[jt]
    for f in rule["required"]:
        if f not in inp:
            errs.append(f"input.{f} 缺失（job_type={jt} 必填，规则来自 task.schema.json）")
    for parent, fields in rule["nested"].items():
        if parent in inp:
            miss = _missing_nested(inp[parent], fields)
            if miss:
                errs.append(f"input.{parent} 缺少必填字段：{miss}")

    repo = inp.get("repository") or {}
    if "commit" in repo and not is_sha40(repo.get("commit")):
        errs.append(f"repository.commit 必须是完整 40 位 SHA，实际 {repo.get('commit')!r}")
    if "url" in repo and not str(repo["url"]).startswith(("https://", "git@")):
        errs.append(f"repository.url 形式可疑：{repo['url']!r}")

    if jt == "INCREMENTAL_CHECK":
        base = inp.get("base_commit")
        bl = inp.get("baseline")
        if base and not is_sha40(base):
            errs.append(f"input.base_commit 必须是完整 40 位 SHA，实际 {base!r}")
        if isinstance(bl, dict):
            if bl.get("commit") and not is_sha40(bl["commit"]):
                errs.append(f"baseline.commit 必须是完整 40 位 SHA，实际 {bl['commit']!r}")
            if base and bl.get("commit") and bl["commit"] != base:
                errs.append(f"baseline.commit ({str(bl['commit'])[:8]}…) 与 base_commit "
                            f"({str(base)[:8]}…) 不一致：历史图必须可追溯到 base commit")
            cfg = inp.get("configuration_id")
            bcfg = bl.get("configuration_id")
            if not bcfg:
                errs.append("baseline.configuration_id 必填：缺少它无法证明基线与本次使用同一构建配置")
            elif cfg and bcfg != cfg:
                errs.append(f"baseline.configuration_id ({bcfg}) 与 input."
                            f"configuration_id ({cfg}) 不一致：依赖图与构建配置强绑定，"
                            "配置不同则结果不可比")
            if bl.get("actual_graph_uri") and not is_artifact_uri(bl["actual_graph_uri"]):
                errs.append(f"baseline.actual_graph_uri 必须为三段式 artifact:// 引用"
                            f"（artifact://<group>/<job_id>/<name>），实际 {bl['actual_graph_uri']!r}")

    if jt == "REPAIR":
        if inp.get("md_report_uri") and not is_artifact_uri(inp["md_report_uri"]):
            errs.append("input.md_report_uri 必须为三段式 artifact:// 引用")
        if inp.get("makefile_uri") and not isinstance(inp["makefile_uri"], str):
            errs.append("input.makefile_uri 必须是字符串")

    return errs


# ================================================================ 校验：发现
def validate_finding(fd, job_type):
    errs = []
    if fd.get("type") not in ("MISSING", "REDUNDANT"):
        errs.append(f"finding.type 非法：{fd.get('type')!r}")
    for k in ("target", "dependency", "detector"):
        if not fd.get(k):
            errs.append(f"finding.{k} 必填")
    if fd.get("commit") and not is_sha40(fd["commit"]):
        errs.append(f"finding.commit 必须是完整 40 位 SHA，实际 {str(fd.get('commit'))[:12]!r}")
    if fd.get("origin") and fd["origin"] not in ("NEW", "CARRIED_OVER", "RESOLVED"):
        errs.append(f"finding.origin 非法：{fd.get('origin')!r}")
    if fd.get("origin") and job_type != "INCREMENTAL_CHECK":
        errs.append(f"finding.origin 仅对 INCREMENTAL_CHECK 有意义（本响应 job_type={job_type}）")
    ev = fd.get("evidence") or {}
    if fd.get("type") == "MISSING" and ev and not (ev.get("actual_read") and not ev.get("declared")):
        errs.append("MISSING 的 evidence 应为 actual_read:true 且 declared:false")
    if fd.get("type") == "REDUNDANT" and ev and not (not ev.get("actual_read") and ev.get("declared")):
        errs.append("REDUNDANT 的 evidence 应为 actual_read:false 且 declared:true")
    return errs


# ================================================================ 校验：delta
def validate_delta(delta, job_type):
    errs = []
    if job_type != "INCREMENTAL_CHECK":
        errs.append(f"output.delta 仅对 INCREMENTAL_CHECK 有意义，本响应 job_type={job_type}")
    if not isinstance(delta, dict):
        return errs + ["output.delta 必须为对象"]
    if not is_sha40(delta.get("baseline_commit")):
        errs.append("delta.baseline_commit 必须是完整 40 位 SHA（标明相对哪条基线）")
    for key in ("added", "removed"):
        val = delta.get(key)
        if not isinstance(val, list):
            errs.append(f"delta.{key} 必须是数组")
            continue
        for i, e in enumerate(val):
            if not isinstance(e, dict) or not e.get("target") or not e.get("dependency"):
                errs.append(f"delta.{key}[{i}] 必须含 target 与 dependency")
            elif not isinstance(e.get("declared"), bool):
                errs.append(f"delta.{key}[{i}].declared 必须是布尔值"
                            "（标明该依赖是否已声明；true 表示合法变化，只在 delta 出现）")
    return errs


# ================================================================ 校验：响应
def validate_job_response(doc):
    errs = []
    for k in ("job_id", "job_type", "status"):
        if not doc.get(k):
            errs.append(f"{k} 必填")
    jt = doc.get("job_type")
    if jt not in JOB_TYPES:
        errs.append(f"job_type 非法：{jt!r}")
        return errs
    status = doc.get("status")
    if status not in STATUSES:
        errs.append(f"status 非法：{status!r}")

    err = doc.get("error")
    out = doc.get("output") or {}
    findings = out.get("findings") or []

    if err:
        if not isinstance(err, dict):
            errs.append("error 必须为对象或 null")
        else:
            if err.get("code") not in ERROR_CODES:
                errs.append(f"error.code 非法：{err.get('code')!r}")
            if not err.get("message"):
                errs.append("error.message 必填")
        if findings:
            errs.append("同一响应中不得同时出现 error 与 output.findings"
                        "（『工具没跑完』与『检出缺失依赖』是两种不同结果）")
        if status == "SUCCEEDED":
            errs.append("status=SUCCEEDED 时不应携带 error（终态语义矛盾）")

    for fd in findings:
        errs.extend(validate_finding(fd, jt))

    for art in out.get("artifacts") or []:
        if art.get("type") and art["type"] not in ARTIFACT_TYPES:
            errs.append(f"artifact.type 非法：{art.get('type')!r}")
        if not is_artifact_uri(art.get("uri")):
            errs.append(f"artifact.uri 必须为三段式 artifact:// 引用，实际 {art.get('uri')!r}")

    if out.get("delta") is not None:
        errs.extend(validate_delta(out["delta"], jt))

    if out.get("current_graph_uri") is not None:
        if jt != "INCREMENTAL_CHECK":
            errs.append(f"output.current_graph_uri 仅对 INCREMENTAL_CHECK 有意义（job_type={jt}）")
        if not is_artifact_uri(out["current_graph_uri"]):
            errs.append("output.current_graph_uri 必须为三段式 artifact:// 引用")

    return errs


def validate_error_entry(e):
    """errors 数组里的系统错误条目。

    边界定义：errors[] 条目【不是完整 Job】，而是"任务以失败终态结束时的对外视图"，
    包含 job_id/job_type/status/error 与可选的 execution、artifacts；
    它【不含】input 回显，也【不含】output.findings —— 因为失败任务没有分析结论。
    """
    errs = []
    if not e.get("job_id"):
        errs.append("job_id 必填")
    if e.get("status") not in ("FAILED", "TIMED_OUT"):
        errs.append(f"系统错误条目的 status 应为 FAILED/TIMED_OUT，实际 {e.get('status')!r}")
    if e.get("job_type") not in JOB_TYPES:
        errs.append(f"job_type 非法：{e.get('job_type')!r}")
    err = e.get("error") or {}
    if err.get("code") not in ERROR_CODES:
        errs.append(f"error.code 非法：{err.get('code')!r}")
    if not err.get("message"):
        errs.append("error.message 必填")
    if (e.get("output") or {}).get("findings"):
        errs.append("系统错误条目不得携带 findings")
    return errs


# ================================================================ 第二部分：负向对照
_DELETE = object()


def _mutate(doc, path, value=_DELETE):
    d = copy.deepcopy(doc)
    cur = d
    for k in path[:-1]:
        cur = cur[k]
    if value is _DELETE:
        cur.pop(path[-1], None)
    else:
        cur[path[-1]] = value
    return d


def _apply(doc, fn):
    d = copy.deepcopy(doc)
    fn(d)
    return d


def build_negative_cases(ex):
    """15 项负向对照：取【完整合法样例】，只改一处，期望被拒绝。

    只改一处是关键 —— 否则无法回答"是这个改动导致拒绝的吗"。
    """
    inc = ex["requests"]["INCREMENTAL_CHECK"]
    full = ex["requests"]["FULL_CHECK"]
    qfull = ex["responses"]["query_full_check"]
    qinc = ex["responses"]["query_incremental_check"]
    zero = "0" * 40
    cases = []

    def add(name, doc, kind, why):
        cases.append({"name": name, "doc": doc, "kind": kind, "why": why})

    # ---- 请求侧 10 项 ----
    add("job_type 改为未定义值 ABC",
        _mutate(full, ["job_type"], "ABC"), "request", "枚举外取值必须拒绝（课堂检查 02）")
    add("删除 baseline",
        _mutate(inc, ["input", "baseline"]), "request", "缺基线无法计算变化（课堂检查 03）")
    add("删除 build_environment_hash",
        _mutate(inc, ["input", "build_environment_hash"]), "request", "无法证明基线与本次同环境")
    add("删除 configuration_id",
        _mutate(inc, ["input", "configuration_id"]), "request", "无对照物时该规则会静默失效")
    add("baseline.commit 与 base_commit 不一致",
        _mutate(inc, ["input", "baseline", "commit"], zero), "request", "历史图必须可追溯到 base commit")
    add("baseline.configuration_id 与本次不一致",
        _mutate(inc, ["input", "baseline", "configuration_id"], "cc-OTHER"), "request", "依赖图与构建配置强绑定")
    add("repository.commit 用 7 位短 SHA",
        _mutate(full, ["input", "repository", "commit"], "abc1234"), "request", "拒绝短 SHA")
    add("请求中携带 job_id",
        _mutate(full, ["job_id"], "job-x"), "request", "job_id 必须由服务端生成")
    add("图引用不是 artifact://",
        _mutate(inc, ["input", "baseline", "actual_graph_uri"], "/local/graph.json"), "request", "大产物必须走引用")
    add("图引用只有两段（缺 name）",
        _mutate(inc, ["input", "baseline", "actual_graph_uri"], "artifact://a11"), "request", "URI 必须三段式（ADR-002）")

    # ---- 响应侧 5 项 ----
    add("delta 出现在全量检测响应中",
        _apply(qfull, lambda d: d["output"].update(
            {"delta": {"baseline_commit": zero, "added": [], "removed": []}})),
        "response", "全量检测没有基线概念")
    add("delta 项缺 declared 标志",
        _apply(qinc, lambda d: d["output"]["delta"]["added"][0].pop("declared", None)),
        "response", "无法区分合法变化与缺失依赖")
    add("error 与 findings 共存",
        _apply(qfull, lambda d: d.update(
            {"status": "FAILED", "error": {"code": "ANALYSIS_5001", "message": "x"}})),
        "response", "检查 04：两种结果不得混在一条响应里")
    add("产物 uri 不是 artifact://",
        _apply(qfull, lambda d: d["output"]["artifacts"][0].update({"uri": "/local/a.json"})),
        "response", "产物必须走引用")
    add("status=SUCCEEDED 却携带 error",
        _apply(qinc, lambda d: d.update(
            {"error": {"code": "EXEC_4002", "message": "timeout"}})),
        "response", "终态语义矛盾")
    return cases


# ================================================================ 第三部分：jsonschema 交叉校验
def jsonschema_results(examples, schema):
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return None
    defs = schema["$defs"]
    v_req = Draft202012Validator({"$ref": "#/$defs/CreateJobRequest", "$defs": defs})
    v_job = Draft202012Validator({"$ref": "#/$defs/Job", "$defs": defs})
    v_accept = Draft202012Validator({"$ref": "#/$defs/DraftResponse", "$defs": defs})
    out = []
    for name, req in examples["requests"].items():
        e = [f"{list(x.path)}: {x.message}" for x in v_req.iter_errors(req)]
        out.append((not e, f"请求 {name}", e))
    for name, resp in examples["responses"].items():
        if "job_id" not in resp:
            continue
        # 202 受理响应只需 job_id + status；查询响应必须满足完整 Job（input 回显 + output）
        v = v_job if ("output" in resp or "input" in resp) else v_accept
        e = [f"{list(x.path)}: {x.message}" for x in v.iter_errors(resp)]
        out.append((not e, f"响应 {name}", e))
    return out


# ================================================================ 主流程
BAR = "=" * 78


def main():
    with open(EXAMPLES_PATH, encoding="utf-8") as f:
        examples = json.load(f)

    part1, part2, part3 = [], [], []

    # ---------- 第一部分：契约检查 ----------
    for name, req in examples["requests"].items():
        errs = validate_request(req, expect_type=name)
        part1.append((not errs, f"请求 · {name}", errs))
    for name, resp in examples["responses"].items():
        errs = validate_job_response(resp)
        part1.append((not errs, f"响应 · {name}", errs))
    for i, e in enumerate(examples.get("errors", []), 1):
        errs = validate_error_entry(e)
        code = (e.get("error") or {}).get("code")
        part1.append((not errs, f"系统错误 · {i} · {code}", errs))
    for case in examples.get("invalid", []):
        data = case["data"]
        errs = (validate_request(data) if "input" in data else validate_job_response(data))
        # 非法样例必须被拒绝
        part1.append((bool(errs), f"非法样例 · {case['case']}",
                      errs if errs else ["✗ 该非法样例竟然通过了！"]))

    # ---------- 第二部分：负向对照 ----------
    for i, c in enumerate(build_negative_cases(examples), 1):
        doc, kind = c["doc"], c["kind"]
        errs = (validate_request(doc) if kind == "request" else validate_job_response(doc))
        part2.append((bool(errs), f"{i:>2}. {c['name']}", c["why"],
                      errs if errs else ["✗ 篡改后竟然仍被接受 —— 该规则形同虚设！"]))

    # ---------- 第三部分：jsonschema 交叉校验 ----------
    js = jsonschema_results(examples, SCHEMA)
    if js is not None:
        for ok, name, errs in js:
            part3.append((ok, name, errs))

    # ---------- 输出 ----------
    print("E2 契约校验（A11 组）")
    print(f"  契约：task.schema.json（{SCHEMA_VERSION}）    样例：contract-examples.json")
    print(f"  必填规则来源：task.schema.json 的 $defs（本脚本不重复定义）")
    print(BAR)

    def dump(results, title, subtitle, note_when_ok):
        print(f"\n【{title}】{subtitle}")
        bad = 0
        for item in results:
            ok, name, *rest = item
            if not ok:
                bad += 1
            extra = rest[0] if rest else ""
            detail = rest[-1] if len(rest) > 1 else []
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
                  + (f"  （{extra}）" if extra and ok else ""))
            for e in (detail if not ok else []):
                print(f"          · {e}")
        print(f"  —— 小计：{len(results) - bad}/{len(results)} 项"
              + ("全部通过" if bad == 0 else f"，{bad} 项失败"))
        return bad

    fails = 0
    fails += dump(part1, "第一部分", "契约检查（零依赖，随包可复算）", "")
    fails += dump(part2, "第二部分", "负向对照 · 篡改完整合法样例且只改一处，期望被拒绝（零依赖）", "")
    if part3:
        fails += dump(part3, "第三部分", "jsonschema 标准 Schema 交叉校验（可选）", "")
    else:
        print("\n【第三部分】jsonschema 标准 Schema 交叉校验（可选）")
        print("  [SKIP] 未安装 jsonschema 库 —— 本脚本不依赖它，跳过不影响结论")

    total = len(part1) + len(part2) + len(part3)
    print("\n" + BAR)
    print("检查 04：『检出缺失依赖』≠『工具执行失败』")
    print("  · status=SUCCEEDED + output.findings → 分析正常完成，检出 MD/RD（允许 findings 为空）")
    print("  · status=FAILED/TIMED_OUT + error.code → 工具没跑完（ENV_3002 / EXEC_4002 / ANALYSIS_5001）")
    print("  · 二者不得同时出现，校验器对混合响应报错（见第二部分用例 13）。")
    print("\n检查 05：findings 与 delta 必须正交")
    print("  · findings 记录『错误状态』（MISSING/REDUNDANT + origin 沿袭/新增/已消除）")
    print("  · delta   记录『依赖边变化』（baseline_commit + added/removed + declared）")
    print("  · declared=true 的变化是【合法变化】，只在 delta 出现 —— 这是 delta 的独立价值")
    print("  · delta 出现在非 INCREMENTAL_CHECK 响应中即报错（见第二部分用例 11）")
    print("  · 注意：delta 是否已退化为『复述 findings』属语义问题，结构校验无法自动判定，由 ADR-006 约束")
    print("\n检查 06：基线一致性（跨字段，JSON Schema 无法表达，由本脚本兜住）")
    print("  · baseline.commit 必须等于 base_commit")
    print("  · baseline.configuration_id 必须等于 input.configuration_id")
    print("\n" + BAR)
    print(f"合计：{total - fails}/{total} 项通过"
          + ("，全部通过" if fails == 0 else f"，{fails} 项失败"))
    print(f"  · 零依赖部分：{len(part1)} + {len(part2)} = {len(part1) + len(part2)} 项"
          + (f"；jsonschema 可选部分：{len(part3)} 项" if part3
             else "；jsonschema 可选部分：未执行（未安装该库）"))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
