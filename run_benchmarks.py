#!/usr/bin/env python3
"""run_benchmarks.py — Discover and run RyuSim benchmarks."""

import argparse
import json
import sys
from pathlib import Path

BENCHMARK_DIRS = [Path("rtlmeter"), Path("cocotb")]


def discover_designs():
    """Scan benchmark directories for designs with config.yaml."""
    designs = []
    for base in BENCHMARK_DIRS:
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and (entry / "config.yaml").exists():
                designs.append(entry)
    return designs


def run_benchmark(design_path, test_name=None, compare_verilator=False):
    """Run benchmark for a single design. Stub — returns placeholder result."""
    return {
        "design": design_path.name,
        "path": str(design_path),
        "test": test_name,
        "compare_verilator": compare_verilator,
        "status": "not_implemented",
        "message": f"Benchmark runner not yet implemented for {design_path.name}",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Discover and run RyuSim benchmarks",
    )
    parser.add_argument("--all", action="store_true", help="Run all benchmarks")
    parser.add_argument("--design", type=str, help="Run specific design")
    parser.add_argument("--test", type=str, help="Run specific test within a design")
    parser.add_argument(
        "--compare-verilator",
        action="store_true",
        help="Enable Verilator comparison",
    )
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument("--ryusim-version", type=str, help="Expected RyuSim version")
    args = parser.parse_args()

    if not args.all and not args.design:
        parser.print_help()
        sys.exit(0)

    designs = discover_designs()

    if args.design:
        designs = [d for d in designs if d.name == args.design]
        if not designs:
            print(f"Error: design '{args.design}' not found", file=sys.stderr)
            sys.exit(1)

    results = []
    for design in designs:
        result = run_benchmark(
            design,
            test_name=args.test,
            compare_verilator=args.compare_verilator,
        )
        results.append(result)

    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "not_implemented": sum(
            1 for r in results if r["status"] == "not_implemented"
        ),
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
