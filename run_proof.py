from __future__ import annotations
import argparse
import json
from pathlib import Path
from veritas_surface.runtime import run_proof

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Veritas public proof surface.")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--stress", type=int, default=0)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    report = run_proof(stress=args.stress)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True))
    if not args.quiet:
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
