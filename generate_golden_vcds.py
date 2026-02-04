#!/usr/bin/env python3
"""generate_golden_vcds.py -- Generate golden VCD files using Verilator."""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path

TESTS_DIR = Path("tests")
GOLDEN_DIR = Path("golden")


def generate_golden(test_path, force=False):
    """Run a test with Verilator and copy the VCD to golden/."""
    rel_path = test_path.relative_to(TESTS_DIR)
    golden_path = GOLDEN_DIR / rel_path

    # Check for existing golden
    vcd_files = list(golden_path.glob("*.vcd"))
    if vcd_files and not force:
        print(f"  SKIP {rel_path} (golden exists, use --force to regenerate)")
        return True

    # Check Verilator is available
    if not shutil.which("verilator"):
        print("Error: verilator not found on PATH", file=sys.stderr)
        return False

    # Check test has a Makefile
    makefile = test_path / "Makefile"
    if not makefile.exists():
        print(f"  SKIP {rel_path} (no Makefile)")
        return True

    print(f"  GENERATING {rel_path}...")

    # Run with Verilator
    result = subprocess.run(
        ["make", "SIM=verilator", "WAVES=1"],
        cwd=str(test_path),
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"  FAIL {rel_path}: {result.stderr[:200]}")
        return False

    # Find VCD output
    sim_build = test_path / "sim_build"
    vcd_candidates = list(sim_build.glob("*.vcd")) + list(test_path.glob("*.vcd"))

    if not vcd_candidates:
        print(f"  FAIL {rel_path}: no VCD file generated")
        return False

    # Copy to golden directory
    golden_path.mkdir(parents=True, exist_ok=True)
    for vcd in vcd_candidates:
        dest = golden_path / vcd.name
        shutil.copy2(vcd, dest)
        print(f"  OK {rel_path} -> {dest}")

    # Clean up sim_build
    subprocess.run(["make", "clean"], cwd=str(test_path), capture_output=True)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate golden VCD files using Verilator as reference simulator"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Generate for specific category (e.g., sequential)",
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Generate for specific test (e.g., sequential/basic_flops/d_ff)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate for all tests with Makefiles"
    )
    parser.add_argument(
        "--force", action="store_true", help="Regenerate even if golden exists"
    )
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
    elif args.category:
        cat_dir = TESTS_DIR / args.category
        if not cat_dir.is_dir():
            print(f"Error: category '{args.category}' not found", file=sys.stderr)
            sys.exit(1)
        tests = sorted(p.parent for p in cat_dir.rglob("config.yaml"))
    else:
        tests = sorted(p.parent for p in TESTS_DIR.rglob("config.yaml"))

    print(f"Generating golden VCDs for {len(tests)} tests...")

    passed = 0
    failed = 0
    for test in tests:
        if generate_golden(test, force=args.force):
            passed += 1
        else:
            failed += 1

    print(f"\nDone: {passed} succeeded, {failed} failed")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
