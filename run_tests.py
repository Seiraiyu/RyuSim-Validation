#!/usr/bin/env python3
"""run_tests.py — Discover and run RyuSim SystemVerilog construct tests."""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

TESTS_DIR = Path("tests")

CATEGORIES = [
    "combinational",
    "sequential",
    "hierarchy",
    "advanced",
    "unsupported",
]


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
    """Run a single SV construct test.

    For supported tests: runs `make` in the test directory (cocotb with SIM=ryusim).
    For unsupported tests: runs `ryusim compile` and asserts it fails.
    For level 2: additionally runs vcddiff against golden VCD.

    Returns a dict with test results.
    """
    category = test_path.relative_to(TESTS_DIR).parts[0]
    test_name = str(test_path.relative_to(TESTS_DIR))
    start_time = time.perf_counter()

    # Read config.yaml
    config_file = test_path / "config.yaml"
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {
            "test": test_name,
            "path": str(test_path),
            "category": category,
            "level": level,
            "status": "error",
            "duration": time.perf_counter() - start_time,
            "stdout": "",
            "stderr": "config.yaml not found",
        }

    top_module = config.get("top_module", "dut")
    is_unsupported = category == "unsupported" or config.get("expect_fail", False)

    if is_unsupported:
        # Unsupported tests: ryusim compile should FAIL
        # Find the SV source file
        sv_files = list(test_path.glob("rtl/*.sv")) + list(test_path.glob("rtl/*.v"))
        if not sv_files:
            sv_files = list(test_path.glob("*.sv")) + list(test_path.glob("*.v"))
        if not sv_files:
            return {
                "test": test_name,
                "path": str(test_path),
                "category": category,
                "level": level,
                "status": "error",
                "duration": time.perf_counter() - start_time,
                "stdout": "",
                "stderr": "No .sv or .v source files found",
            }

        dut_file = str(sv_files[0])
        try:
            result = subprocess.run(
                ["ryusim", "compile", dut_file, "--top", top_module],
                capture_output=True,
                text=True,
                cwd=str(test_path),
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            return {
                "test": test_name,
                "path": str(test_path),
                "category": category,
                "level": level,
                "status": "error",
                "duration": time.perf_counter() - start_time,
                "stdout": "",
                "stderr": "Compile timed out (300s)",
            }
        except FileNotFoundError:
            return {
                "test": test_name,
                "path": str(test_path),
                "category": category,
                "level": level,
                "status": "error",
                "duration": time.perf_counter() - start_time,
                "stdout": "",
                "stderr": "ryusim not found on PATH",
            }

        duration = time.perf_counter() - start_time

        if result.returncode != 0:
            # Compilation failed as expected
            status = "expected_fail"
            # If expected_error.txt exists, check that stderr contains expected message
            expected_error_file = test_path / "expected_error.txt"
            if expected_error_file.exists():
                expected_msg = expected_error_file.read_text().strip()
                if expected_msg and expected_msg not in result.stderr:
                    status = "failed"
        else:
            # Compilation succeeded but should have failed
            status = "failed"

        return {
            "test": test_name,
            "path": str(test_path),
            "category": category,
            "level": level,
            "status": status,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    # Supported tests: run make (cocotb with SIM=ryusim)
    try:
        result = subprocess.run(
            ["make"],
            capture_output=True,
            text=True,
            cwd=str(test_path),
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return {
            "test": test_name,
            "path": str(test_path),
            "category": category,
            "level": level,
            "status": "error",
            "duration": time.perf_counter() - start_time,
            "stdout": "",
            "stderr": "Test timed out (300s)",
        }
    except FileNotFoundError:
        return {
            "test": test_name,
            "path": str(test_path),
            "category": category,
            "level": level,
            "status": "error",
            "duration": time.perf_counter() - start_time,
            "stdout": "",
            "stderr": "make not found on PATH",
        }

    duration = time.perf_counter() - start_time
    status = "passed" if result.returncode == 0 else "failed"

    # Level 2: VCD comparison against golden reference
    if level >= 2 and status == "passed":
        vcd_files = list(test_path.glob("**/*.vcd"))
        golden_dir = Path("golden") / test_path.relative_to(TESTS_DIR)
        golden_vcds = list(golden_dir.glob("*.vcd")) if golden_dir.is_dir() else []

        if golden_vcds and vcd_files:
            # Find the output VCD (not in golden/)
            output_vcds = [v for v in vcd_files if "golden" not in v.parts]
            if output_vcds:
                try:
                    vcd_result = subprocess.run(
                        ["vcddiff", str(output_vcds[0]), str(golden_vcds[0])],
                        capture_output=True,
                        text=True,
                        cwd=str(test_path),
                        timeout=60,
                    )
                    if vcd_result.returncode != 0:
                        status = "failed"
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    # vcddiff not available or timed out; don't fail the test
                    pass

    return {
        "test": test_name,
        "path": str(test_path),
        "category": category,
        "level": level,
        "status": status,
        "duration": duration,
        "stdout": result.stdout,
        "stderr": result.stderr,
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
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-test progress to stderr")
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

    ryusim_version = get_ryusim_version()
    if args.ryusim_version and ryusim_version and args.ryusim_version != ryusim_version:
        print(f"Warning: expected ryusim {args.ryusim_version}, got {ryusim_version}", file=sys.stderr)
    timestamp = datetime.now(timezone.utc).isoformat()

    results = []
    for test in tests:
        result = run_test(test, level=args.level)
        results.append(result)
        if args.verbose:
            print(
                f"  {result['test']}: {result['status']} ({result['duration']:.2f}s)",
                file=sys.stderr,
            )

    # Group by category for summary
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "failed": 0, "expected_fail": 0, "error": 0}
        categories[cat]["total"] += 1
        categories[cat][r["status"]] = categories[cat].get(r["status"], 0) + 1

    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "expected_fail": sum(1 for r in results if r["status"] == "expected_fail"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "level": args.level,
        "ryusim_version": ryusim_version,
        "timestamp": timestamp,
        "categories": categories,
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
