"""CLI demo with an explicit approval flag; safe by default."""
import argparse
import json
from pathlib import Path
from .service import ReviewService

def main():
    parser = argparse.ArgumentParser(description="RepoMedic AI — reproducible agentic repair demo")
    parser.add_argument("command", choices=["demo"])
    parser.add_argument("--approve", action="store_true", help="Explicitly approve patch export")
    parser.add_argument("--output", default="artifacts", help="Artifact output directory")
    parser.add_argument("--json", action="store_true", help="Machine-readable result")
    args = parser.parse_args()
    service = ReviewService()
    record = service.start()
    if args.approve:
        record = service.approve(record["run_id"], True, Path(args.output))
    if args.json:
        print(json.dumps(record, indent=2))
        return
    print("\nRepoMedic AI | Multi-Agent Repair Demo")
    print("=" * 44)
    print("ISSUE:", record["issue"])
    for event in record["trace"]:
        print(f"[{event['agent'].upper()}] {event['event']}")
    print("BASELINE TESTS: FAIL" if not record["baseline"]["passed"] else "BASELINE TESTS: PASS")
    print("PATCHED TESTS: PASS" if record["verification"]["passed"] else "PATCHED TESTS: FAIL")
    print("\nPROPOSED PATCH:\n", record["diff"])
    print("DECISION:", record["decision"])
    if args.approve:
        print("PATCH FILE:", record["patch_file"])
    else:
        print("No patch released. Rerun with --approve after reviewing the diff.")

if __name__ == "__main__":
    main()
