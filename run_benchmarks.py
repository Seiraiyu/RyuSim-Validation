#!/usr/bin/env python3
"""run_benchmarks.py — Discover and run RyuSim benchmarks."""

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

BENCHMARK_DIRS = {
    "rtlmeter": Path("rtlmeter_tests"),
    "cocotb": Path("cocotb_tests"),
}
DEFAULT_TIMEOUT = 900  # 15 minutes — large designs need 5-10min to compile on CI


def host_platform():
    """'<ID>-<VERSION_ID>' from os-release, e.g. 'debian-12' — matches CI matrix names."""
    try:
        info = platform.freedesktop_os_release()
    except (OSError, AttributeError):  # AttributeError: Python < 3.10 (Rocky 9)
        return ""
    return f"{info.get('ID', '')}-{info.get('VERSION_ID', '')}"


def apply_expected_fail(result, design_path, host):
    """`expected_fail: {platforms: [...], reason: ...}` in config.yaml inverts the
    check on those platforms — like run_tests.py's `expected: fail`, it tracks a
    known RyuSim issue, and an unexpected pass means the issue was fixed."""
    try:
        with open(design_path / "config.yaml") as f:
            xfail = (yaml.safe_load(f) or {}).get("expected_fail") or {}
    except (FileNotFoundError, yaml.YAMLError):
        return
    if host in xfail.get("platforms", []):
        result["expected_fail_reason"] = xfail.get("reason", "")
        if result["status"] == "passed":
            result["status"] = "failed"
        elif result["status"] == "failed":
            result["status"] = "expected_fail"


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


def discover_designs(include_disabled=False, source=None):
    """Scan benchmark directories for designs with config.yaml.

    Args:
        include_disabled: If True, include designs with enabled: false
        source: If set, only scan this source directory ("cocotb" or "rtlmeter")
    """
    designs = []
    if source:
        dirs_to_scan = [BENCHMARK_DIRS[source]]
    else:
        dirs_to_scan = list(BENCHMARK_DIRS.values())
    for base in dirs_to_scan:
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


def run_native_benchmark(design_path, config, test_name=None, tags=None,
                         compare_verilator=False, timeout_override=None):
    """Run a native-testbench design: `make compile`, then `make test-<t>` per test.

    Pass/fail per test is the Makefile contract: sim exit 0 AND pass marker
    (design doc 2026-08-08 §4.3). Returns the same top-level result shape as
    run_benchmark, plus a per-test "tests" list.
    """
    design_timeout = timeout_override or config.get("timeout", DEFAULT_TIMEOUT)

    tests_cfg = config.get("tests") or {}
    if test_name:
        if test_name not in tests_cfg:
            return _error_result(design_path, test_name,
                                 f"test '{test_name}' not in config.yaml tests")
        selected = [test_name]
    else:
        selected = [
            t for t, tc in tests_cfg.items()
            if not tags or set(tags) & set((tc or {}).get("tags", []))
        ]

    start = time.perf_counter()
    try:
        compile_res = subprocess.run(
            ["make", "compile"], capture_output=True, text=True,
            cwd=str(design_path), timeout=design_timeout,
        )
    except subprocess.TimeoutExpired:
        return _error_result(design_path, test_name,
                             f"compile timed out ({design_timeout}s)",
                             elapsed=time.perf_counter() - start)
    compile_elapsed = time.perf_counter() - start

    tests = []
    if compile_res.returncode == 0:
        for t in selected:
            t_start = time.perf_counter()
            try:
                t_res = subprocess.run(
                    ["make", f"test-{t}"], capture_output=True, text=True,
                    cwd=str(design_path), timeout=design_timeout,
                )
                t_status = "passed" if t_res.returncode == 0 else "failed"
                t_tail = t_res.stdout[-2000:]
            except subprocess.TimeoutExpired:
                t_status, t_tail = "timeout", ""
            tests.append({
                "name": t,
                "status": t_status,
                "elapsed": time.perf_counter() - t_start,
                "tags": (tests_cfg.get(t) or {}).get("tags", []),
                "stdout_tail": t_tail,
            })

    total = time.perf_counter() - start
    if compile_res.returncode != 0:
        status = "failed"
    elif all(t["status"] == "passed" for t in tests):
        status = "passed"
    else:
        status = "failed"

    result = {
        "design": design_path.name,
        "path": str(design_path),
        "test": test_name,
        "top_module": config.get("top_module"),
        "description": config.get("description"),
        "mode": "native",
        "ryusim": {
            "elapsed": total,
            "status": status,
            "compile": {"elapsed": compile_elapsed,
                        "status": "passed" if compile_res.returncode == 0 else "failed"},
            "execute": None,
        },
        "tests": tests,
        "status": status,
        "duration": total,
        "stdout": compile_res.stdout[-2000:],
        "stderr": compile_res.stderr[-2000:],
    }
    if compare_verilator:
        # Native Verilator comparison lands in a later phase (design doc §4.5).
        result["verilator"] = {"status": "unsupported-native"}
    return result


def _error_result(design_path, test_name, message, elapsed=0):
    return {
        "design": design_path.name,
        "path": str(design_path),
        "test": test_name,
        "ryusim": {
            "compile": {"elapsed": elapsed, "status": "error"},
            "execute": {"elapsed": 0, "status": "skipped"},
        },
        "status": "error",
        "duration": elapsed,
        "stdout": "",
        "stderr": message,
    }


def run_benchmark(design_path, test_name=None, compare_verilator=False, timeout_override=None, tags=None):
    """Run benchmark for a single design.

    Runs `make` in the design directory (cocotb with SIM=ryusim), captures
    timing and exit code. Optionally runs Verilator comparison.

    Timeout precedence: CLI --timeout > config.yaml timeout > DEFAULT_TIMEOUT.

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

    if "tb" in config:
        return run_native_benchmark(
            design_path, config, test_name=test_name, tags=tags,
            compare_verilator=compare_verilator, timeout_override=timeout_override,
        )

    # Determine timeout: CLI override > config.yaml > default
    design_timeout = timeout_override or config.get("timeout", DEFAULT_TIMEOUT)

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
            timeout=design_timeout,
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
            "stderr": f"Benchmark timed out ({design_timeout}s)",
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
                timeout=design_timeout,
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
    parser.add_argument(
        "--source",
        type=str,
        choices=["cocotb", "rtlmeter"],
        help="Only run benchmarks from this source directory",
    )
    parser.add_argument("--test", type=str, help="Run specific test within a design")
    parser.add_argument(
        "--compare-verilator",
        action="store_true",
        help="Enable Verilator comparison",
    )
    parser.add_argument(
        "--tags",
        type=str,
        help="Comma-separated test tags to run (native designs only), e.g. --tags sanity",
    )
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument("--timeout", type=int, help=f"Override per-design timeout in seconds (default: {DEFAULT_TIMEOUT})")
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

    designs = discover_designs(include_disabled=args.include_disabled, source=args.source)

    if args.design:
        designs = [d for d in designs if d.name == args.design]
        if not designs:
            print(f"Error: design '{args.design}' not found", file=sys.stderr)
            sys.exit(1)

    ryusim_version = get_ryusim_version()
    if args.ryusim_version and ryusim_version and args.ryusim_version != ryusim_version:
        print(f"Warning: expected ryusim {args.ryusim_version}, got {ryusim_version}", file=sys.stderr)
    timestamp = datetime.now(timezone.utc).isoformat()

    host = host_platform()
    results = []
    for design in designs:
        result = run_benchmark(
            design,
            test_name=args.test,
            compare_verilator=args.compare_verilator,
            timeout_override=args.timeout,
            tags=[t.strip() for t in args.tags.split(",")] if args.tags else None,
        )
        apply_expected_fail(result, design, host)
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
        "expected_fail": sum(1 for r in results if r["status"] == "expected_fail"),
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
