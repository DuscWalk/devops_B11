["command"]), verify_command=inp["verify_command"], max_iterations=inp.get("max_iterations",1), timeout_seconds=inp.get("timeout_seconds",1200))
def main():
    parser = argparse.ArgumentParser(description="MDFixer")
    parser.add_argument("--request", required=True)
    parser.add_argument("--out-dir", default="out")
    args = parser.parse_args()
    result = run_repair(load_request(args.request), Path(args.out_dir))
    output = {"schema_version":SCHEMA_VERSION, "job_type":"REPAIR", "status":"SUCCEEDED" if result.error is None else "FAILED", "output":{"patch_uri":result.patch_uri, "patch_sha256":result.patch_sha256, "artifacts":result.artifacts, "summary":result.summary}, "error":result.error}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if result.error is None else 1
if __name__ == "__main__": sys.exit(main())
