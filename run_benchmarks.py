#!/usr/bin/env python3
"""run_benchmarks.py — Discover and run RyuSim benchmarks."""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

BENCHMARK_DIRS = [Path("rtlmeter_tests"), Path("cocotb_tests")]


def get_ryusim_version():
    """Get the installed ryusim version string."""
    try:
        result = subprocess.run(
            ["ryusim", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() or result.stderr.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


def discover_designs(include_disabled=False):
    """Scan benchmark directories for designs with config.yaml.

    Args:
        include_disabled: If True, include designs with enabled: false
    """
    designs = []
    for base in BENCHMARK_DIRS:
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            config_file = entry / "config.yaml"
            if entry.is_dir() and config_file.exists():
                # Check if design is enabled (default: True)
                if not include_disabled:
                    try:
                        with open(config_file) as f:
                            config = yaml.safe_load(f) or {}
                        if config.get("enabled", True) is False:
                            continue
                    except (FileNotFoundError, yaml.YAMLError):
                        pass
                designs.append(entry)
    return designs


def run_benchmark(design_path, test_name=None, compare_verilator=False):
    """Run benchmark for a single design.

    Runs `make` in the design directory (cocotb with SIM=ryusim), captures
    timing and exit code. Optionally runs Verilator comparison.

    Returns a dict with benchmark results.
    """
    # Read config.yaml
    config_file = design_path / "config.yaml"
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {
            "design": design_path.name,
            "path": str(design_path),
            "test": test_name,
            "ryusim": {
                "compile": {"elapsed": 0, "status": "error"},
                "execute": {"elapsed": 0, "status": "error"},
            },
            "status": "error",
            "duration": 0,
            "stdout": "",
            "stderr": "config.yaml not found",
        }

    # Build make command with optional test target
    make_cmd = ["make"]
    if test_name:
        make_cmd.append(test_name)

    # Run RyuSim benchmark via make
    compile_start = time.perf_counter()
    try:
        result = subprocess.run(
            make_cmd,
            capture_output=True,
            text=True,
            cwd=str(design_path),
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - compile_start
        return {
            "design": design_path.name,
            "path": str(design_path),
            "test": test_name,
            "ryusim": {
                "compile": {"elapsed": elapsed, "status": "timeout"},
                "execute": {"elapsed": 0, "status": "skipped"},
            },
            "status": "error",
            "duration": elapsed,
            "stdout": "",
            "stderr": "Benchmark timed out (300s)",
        }
    except FileNotFoundError:
        return {
            "design": design_path.name,
            "path": str(design_path),
            "test": test_name,
            "ryusim": {
                "compile": {"elapsed": 0, "status": "error"},
                "execute": {"elapsed": 0, "status": "error"},
            },
            "status": "error",
            "duration": 0,
            "stdout": "",
            "stderr": "make not found on PATH",
        }

    total_elapsed = time.perf_counter() - compile_start
    ryusim_status = "passed" if result.returncode == 0 else "failed"

    benchmark_result = {
        "design": design_path.name,
        "path": str(design_path),
        "test": test_name,
        "top_module": config.get("top_module"),
        "description": config.get("description"),
        "ryusim": {
            "elapsed": total_elapsed,
            "status": ryusim_status,
            "compile": None,
            "execute": None,
        },
        "status": ryusim_status,
        "duration": total_elapsed,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

    # Optional Verilator comparison
    if compare_verilator and ryusim_status == "passed":
        verilator_start = time.perf_counter()
        try:
            verilator_result = subprocess.run(
                ["make", "SIM=verilator"],
                capture_output=True,
                text=True,
                cwd=str(design_path),
                timeout=300,
            )
            verilator_elapsed = time.perf_counter() - verilator_start
            benchmark_result["verilator"] = {
                "compile": {
                    "elapsed": verilator_elapsed,
                    "status": "passed" if verilator_result.returncode == 0 else "failed",
                },
                "execute": {
                    "elapsed": verilator_elapsed,
                    "status": "passed" if verilator_result.returncode == 0 else "failed",
                },
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            verilator_elapsed = time.perf_counter() - verilator_start
            benchmark_result["verilator"] = {
                "compile": {"elapsed": verilator_elapsed, "status": "error"},
                "execute": {"elapsed": 0, "status": "skipped"},
            }

    return benchmark_result


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
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-benchmark progress to stderr")
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        help="Include designs with enabled: false in config.yaml",
    )
    args = parser.parse_args()

    if not args.all and not args.design:
        parser.print_help()
        sys.exit(0)

    designs = discover_designs(include_disabled=args.include_disabled)

    if args.design:
        designs = [d for d in designs if d.name == args.design]
        if not designs:
            print(f"Error: design '{args.design}' not found", file=sys.stderr)
            sys.exit(1)

    ryusim_version = get_ryusim_version()
    if args.ryusim_version and ryusim_version and args.ryusim_version != ryusim_version:
        print(f"Warning: expected ryusim {args.ryusim_version}, got {ryusim_version}", file=sys.stderr)
    timestamp = datetime.now(timezone.utc).isoformat()

    results = []
    for design in designs:
        result = run_benchmark(
            design,
            test_name=args.test,
            compare_verilator=args.compare_verilator,
        )
        results.append(result)
        if args.verbose:
            print(
                f"  {result['design']}: {result['status']} ({result['duration']:.2f}s)",
                file=sys.stderr,
            )

    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "ryusim_version": ryusim_version,
        "timestamp": timestamp,
        "results": results,
    }

    print(json.dumps(summary, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2) + "\n")
        print(f"Results written to {args.output}", file=sys.stderr)

    if summary["failed"] > 0 or summary.get("error", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
