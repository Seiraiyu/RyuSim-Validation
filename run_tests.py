#!/usr/bin/env python3
"""run_tests.py — Discover and run RyuSim SystemVerilog construct tests."""

import argparse
import json
import sys
from pathlib import Path

TESTS_DIR = Path("tests")

CATEGORIES = [
    "combinational",
    "sequential",
    "hierarchy",
    "advanced",
    "unsupported",
]


def discover_tests(category=None):
    """Scan tests directory for test cases with config.yaml."""
    tests = []
    if not TESTS_DIR.is_dir():
        return tests

    search_dirs = []
    if category:
        cat_dir = TESTS_DIR / category
        if cat_dir.is_dir():
            search_dirs.append(cat_dir)
    else:
        for cat in CATEGORIES:
            cat_dir = TESTS_DIR / cat
            if cat_dir.is_dir():
                search_dirs.append(cat_dir)

    for search_dir in search_dirs:
        for config in sorted(search_dir.rglob("config.yaml")):
            tests.append(config.parent)

    return tests


def run_test(test_path, level=1):
    """Run a single SV construct test. Stub — returns placeholder result."""
    category = test_path.relative_to(TESTS_DIR).parts[0]
    return {
        "test": str(test_path.relative_to(TESTS_DIR)),
        "path": str(test_path),
        "category": category,
        "level": level,
        "status": "not_implemented",
        "message": f"Test runner not yet implemented for {test_path.name}",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Discover and run RyuSim SystemVerilog construct tests",
    )
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--category", type=str, choices=CATEGORIES, help="Run specific category")
    parser.add_argument("--test", type=str, help="Run specific test (e.g., combinational/operators/add_sub)")
    parser.add_argument("--level", type=int, default=1, choices=[1, 2], help="Validation level (default: 1)")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument("--ryusim-version", type=str, help="Expected RyuSim version")
    parser.add_argument("--limit", type=int, help="Max number of tests to run")
    args = parser.parse_args()

    if not args.all and not args.category and not args.test:
        parser.print_help()
        sys.exit(0)

    if args.test:
        test_path = TESTS_DIR / args.test
        if not test_path.is_dir():
            print(f"Error: test '{args.test}' not found", file=sys.stderr)
            sys.exit(1)
        tests = [test_path]
    else:
        tests = discover_tests(category=args.category)

    if args.limit:
        tests = tests[: args.limit]

    results = []
    for test in tests:
        result = run_test(test, level=args.level)
        results.append(result)

    # Group by category for summary
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "failed": 0, "not_implemented": 0}
        categories[cat]["total"] += 1
        categories[cat][r["status"]] = categories[cat].get(r["status"], 0) + 1

    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "not_implemented": sum(1 for r in results if r["status"] == "not_implemented"),
        "level": args.level,
        "categories": categories,
        "results": results,
    }

    print(json.dumps(summary, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2) + "\n")
        print(f"Results written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
