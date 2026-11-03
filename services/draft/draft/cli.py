"""命令行入口。

  python3 -m draft version
  python3 -m draft smoke [--fixture fixtures/draft]
  python3 -m draft auto-build --candidate PATH --out DIR --expected-output TEXT

E6 在 E4 的 version/smoke 之外加入 auto-build：两轮真实构建（初始失败 + 候选修复）
与同镜像 ID 的断网运行验证。
"""
import argparse
import json

from . import __version__
from .autobuild import auto_build
from .smoke import run_smoke


def build_parser():
    ap = argparse.ArgumentParser(prog="draft")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("version", help="打印版本")
    sp = sub.add_parser("smoke", help="E4 冒烟测试：在容器里通过宿主机 Docker 构建 E3 的 Dockerfile.broken")
    sp.add_argument("--fixture", default="fixtures/draft")
    sp.add_argument("--tag", default="e4-smoke-broken:latest")
    sp = sub.add_parser("auto-build", help="E6：两轮构建与程序验证")
    sp.add_argument("--fixture", default="fixtures/draft")
    sp.add_argument("--candidate", required=True)
    sp.add_argument("--out", required=True)
    sp.add_argument("--expected-output", required=True)
    sp.add_argument("--timeout", type=int, default=300)
    sp.add_argument("--verify-timeout", type=int, default=30)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.cmd == "version":
        print(f"draft {__version__}")
        return 0
    if args.cmd == "smoke":
        result = run_smoke(args.fixture, args.tag)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["passed"] else 1
    try:
        result = auto_build(args.fixture, args.candidate, args.out, args.expected_output,
                            args.timeout, args.verify_timeout)
    except (ValueError, OSError) as exc:
        result = {"status": "FAILED", "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "SUCCEEDED" else 1
