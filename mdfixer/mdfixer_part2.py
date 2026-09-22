wd=cwd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired: return -1, "", "TIMEOUT"
    except Exception as e: return -1, "", str(e)
def verify_candidate(patch, makefile_path, build_cmd, verify_cmd, workdir):
    original = makefile_path.read_text(encoding="utf-8")
    try:
        makefile_path.write_text(patch, encoding="utf-8")
        build_rc, _, build_err = run_command(build_cmd, cwd=str(workdir))
        if build_rc != 0: return CandidateResult(accepted=False, reason=f"build失败(exit={build_rc}): {build_err[:200]}", patch=patch, build_exit_code=build_rc)
        verify_rc, _, verify_err = run_command(verify_cmd, cwd=str(workdir))
        if verify_rc != 0: return CandidateResult(accepted=False, reason=f"verify失败(exit={verify_rc}): {verify_err[:200]}", patch=patch, build_exit_code=build_rc, verify_exit_code=verify_rc)
        return CandidateResult(accepted=True, patch=patch, build_exit_code=build_rc, verify_exit_code=verify_rc)
    finally: makefile_path.write_text(original, encoding="utf-8")
def sha256_hex(data): return hashlib.sha256(data).hexdigest()
def run_repair(rep_input, out_dir):
    result = RepairResult()
    try: findings = load_md_report(rep_input.md_report_uri)
    except Exception as e: result.error = {"code":"ANALYSIS_5001","message":"读取MD报告失败","detail":str(e)}; return result
    missing_findings = filter_missing(findings)
    if not missing_findings:
        result.summary = {"candidates_total":0,"candidates_accepted":0,"candidates_rejected":0,"missing_fixed":0,"recheck_missing_remaining":0}
        return result
    makefile_info = parse_makefile_uri(rep_input.makefile_uri)
    if makefile_info is None:
        result.error = {"code":"VALIDATION_4001","message":"makefile_uri格式不正确","detail":f"期望repo://<sha>/<path>，实际:{rep_input.makefile_uri}"}
        return result
    makefile_path = out_dir / "workspace" / makefile_info[1]
    if not makefile_path.exists(): makefile_path = Path(makefile_info[1])
    if not makefile_path.exists():
        result.error = {"code":"ENV_3002","message":"找不到Makefile","detail":f"makefile_uri={rep_input.makefile_uri}"}
        return result
    original_content = makefile_path.read_text(encoding="utf-8")
    rules = parse_makefile(original_content)
    style = detect_declaration_style(original_content, rules)
    candidates = []
    current_patched = original_content
    fixed_count = 0
    for finding in missing_findings:
        gen = generate_patch_for_missing(current_patched, rules, finding)
        if gen is None:
            candidates.append(CandidateResult(accepted=False, reason=f"无法为target={finding.target}生成补丁"))
            continue
        patched_content, desc = gen
        diff = make_unified_diff(original_content, patched_content, makefile_info[1])
        cand = verify_candidate(patch=patched_content, makefile_path=makefile_path, build_cmd=rep_input.build.command, verify_cmd=rep_input.verify_command, workdir=makefile_path.parent)
        cand.patch = diff
        cand.description = desc
        if cand.accepted: current_patched = patched_content; fixed_count += 1
        candidates.append(cand)
    accepted = [c for c in candidates if c.accepted]
    rejected = [c for c in candidates if not c.accepted]
    out_dir.mkdir(parents=True, exist_ok=True)
    job_id = f"job-repair-{int(datetime.now().timestamp())}"
    final_patch = make_unified_diff(original_content, current_patched, makefile_info[1])
    patch_bytes = final_patch.encode("utf-8")
    patch_sha = sha256_hex(patch_bytes)
    patch_path = out_dir / "fix.patch"
    patch_path.write_bytes(patch_bytes)
    patch_uri = f"artifact://b11/{job_id}/fix.patch"
    result.patch_uri = patch_uri
    result.patch_sha256 = patch_sha
    style_report = {"declaration_style":style, "targets_found":[r.target for r in rules], "missing_fixed":fixed_count, "missing_total":len(missing_findings), "rejected_reasons":[{"target":c.description, "reason":c.reason} for c in rejected]}
    (out_dir / "declaration_style.json").write_text(json.dumps(style_report, ensure_ascii=False, indent=2), encoding="utf-8")
    test_result = {"candidates_total":len(candidates), "candidates_accepted":len(accepted), "candidates_rejected":len(rejected), "accepted_details":[{"description":c.description, "build_exit_code":c.build_exit_code, "verify_exit_code":c.verify_exit_code} for c in accepted], "rejected_details":[{"description":c.description, "reason":c.reason} for c in rejected]}
    (out_dir / "test_result.json").write_text(json.dumps(test_result, ensure_ascii=False, indent=2), encoding="utf-8")
    result.artifacts = [
        {"artifact_id":f"{job_id}-patch", "type":"PATCH", "uri":patch_uri, "media_type":"text/x-diff", "producer_job_id":job_id, "commit":rep_input.repository.commit, "sha256":patch_sha},
        {"artifact_id":f"{job_id}-style", "type":"STYLE_REPORT", "uri":f"artifact://b11/{job_id}/declaration_style.json", "media_type":"application/json", "producer_job_id":job_id, "commit":rep_input.repository.commit},
        {"artifact_id":f"{job_id}-test", "type":"TEST_RESULT", "uri":f"artifact://b11/{job_id}/test_result.json", "media_type":"application/json", "producer_job_id":job_id, "commit":rep_input.repository.commit}
    ]
    result.summary = {"candidates_total":len(candidates), "candidates_accepted":len(accepted), "candidates_rejected":len(rejected), "missing_fixed":fixed_count, "recheck_missing_remaining":len(missing_findings)-fixed_count}
    return result
def load_request(path):
    with open(path, "r", encoding="utf-8") as f: data = json.load(f)
    inp = data["input"]
    return RepairInput(repository=Repository(url=inp["repository"]["url"], commit=inp["repository"]["commit"]), md_report_uri=inp["md_report_uri"], makefile_uri=inp["makefile_uri"], image=inp["image"], build=BuildSpec(command=inp["build"]