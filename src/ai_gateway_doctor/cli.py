from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .checks import diagnose
from .redact import redact

SYMBOLS = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "skip": "SKIP"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-gateway-doctor")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    diagnose_parser = sub.add_parser("diagnose", help="Run secret-safe, read-only checks")
    diagnose_parser.add_argument("--home", type=Path, help="Home directory to inspect")
    diagnose_parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    home = args.home.expanduser() if args.home else Path.home()
    findings = diagnose(home)
    if args.json:
        output = json.dumps([item.to_dict() for item in findings], indent=2)
    else:
        rows = []
        for item in findings:
            rows.append(f"{SYMBOLS[item.status]:4}  {item.check}: {item.summary}")
            if item.evidence:
                rows.append(f"      evidence: {item.evidence}")
            if item.remediation:
                rows.append(f"      next: {item.remediation}")
        output = "\n".join(rows)
    print(redact(output, home))
    return 1 if any(item.status == "fail" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

