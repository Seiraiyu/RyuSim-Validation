#!/usr/bin/env python3
"""Vendor chipsalliance/UHDM-integration-tests into uhdm_tests/upstream/.

Reads each upstream tests/<Name>/Makefile.in for TOP_FILE/TOP_MODULE, copies
the SV sources (dropping upstream's Verilator/Yosys harness files), and
generates a native-mode config.yaml per test. Re-runnable: refreshes sources
and provenance but preserves an existing config's `expected:`/`reason:` keys.

Usage:
  python3 tools/import_uhdm_tests.py --upstream /path/to/UHDM-integration-tests \
      [--dest uhdm_tests/upstream] [--expected-map smoke-results.txt]

The optional --expected-map file has lines "<TestName> PASS|FAIL ..." (as
produced by the smoke sweep); tests marked FAIL get `expected: fail`.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HARNESS_FILES = {"main.cpp", "task.cpp", "Makefile.in"}
HARNESS_SUFFIXES = {".tcl", ".cpp", ".py"}


def parse_makefile(mk_path):
    """Return (top_files, top_module) from an upstream Makefile.in."""
    text = mk_path.read_text()
    # Join backslash-continued lines (SERV-style multi-file TOP_FILE).
    text = re.sub(r"\\\s*\n", " ", text)
    top_files, top_module = [], None
    for line in text.splitlines():
        m = re.match(r"\s*TOP_FILE\s*:?=\s*(.+)", line)
        if m:
            top_files = [f.replace("$(TEST_DIR)/", "").replace("$(TEST_DIR)", ".")
                         for f in m.group(1).split()]
        m = re.match(r"\s*TOP_MODULE\s*:?=\s*(\S+)", line)
        if m:
            top_module = m.group(1)
        # Some tests pass extra SV sources via VERILATOR_FLAGS
        # (e.g. ParameterDoubleUnderscoreInSvFrontend's top.sv).
        m = re.match(r"\s*VERILATOR_FLAGS\s*:?=\s*(.+)", line)
        if m:
            for tok in m.group(1).split():
                if tok.endswith((".sv", ".v")):
                    top_files.append(
                        tok.replace("$(TEST_DIR)/", "").replace("$(TEST_DIR)", "."))
    return top_files, top_module


def copy_sources(src_dir, dest_dir):
    """Copy test payload, skipping upstream harness files. Returns file list."""
    copied = []
    for p in sorted(src_dir.rglob("*")):
        rel = p.relative_to(src_dir)
        if p.is_dir():
            continue
        if rel.parts[0] in ("build",):
            continue
        if p.name in HARNESS_FILES or p.suffix in HARNESS_SUFFIXES:
            continue
        target = dest_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        copied.append(str(rel))
    return copied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True, type=Path)
    ap.add_argument("--dest", type=Path, default=Path("uhdm_tests/upstream"))
    ap.add_argument("--expected-map", type=Path)
    args = ap.parse_args()

    revision = subprocess.run(
        ["git", "-C", str(args.upstream), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    expected = {}
    if args.expected_map and args.expected_map.exists():
        for line in args.expected_map.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1] in ("PASS", "FAIL"):
                expected[parts[0]] = "pass" if parts[1] == "PASS" else "fail"

    tests_dir = args.upstream / "tests"
    imported, skipped = [], []
    for tdir in sorted(p for p in tests_dir.iterdir() if p.is_dir()):
        name = tdir.name
        mk = tdir / "Makefile.in"
        if not mk.exists():
            skipped.append((name, "no Makefile.in"))
            continue
        top_files, top_module = parse_makefile(mk)
        top_files = [f for f in top_files if (tdir / f).exists()]
        if not top_files or not top_module:
            skipped.append((name, "no TOP_FILE/TOP_MODULE"))
            continue

        dest = args.dest / name
        dest.mkdir(parents=True, exist_ok=True)

        cfg_path = dest / "config.yaml"
        prior = {}
        if cfg_path.exists():
            try:
                prior = yaml.safe_load(cfg_path.read_text()) or {}
            except yaml.YAMLError:
                prior = {}

        # Locally patched tests (invalid upstream sources repaired in-repo)
        # keep their sources; only provenance/config metadata is refreshed.
        if not prior.get("patched"):
            copy_sources(tdir, dest)

        cfg = {
            "name": name,
            "mode": "native",
            "level": "compile",
            "top_module": top_module,
            "sources": top_files,
            "upstream": {
                "repository":
                    "https://github.com/chipsalliance/UHDM-integration-tests.git",
                "revision": revision,
                "path": f"tests/{name}",
            },
            "expected": prior.get("expected", expected.get(name, "pass")),
        }
        if "reason" in prior:
            cfg["reason"] = prior["reason"]
        if prior.get("patched"):
            cfg["patched"] = True
            cfg["sources"] = prior.get("sources", cfg["sources"])
        cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
        imported.append(name)

    print(f"imported {len(imported)} tests -> {args.dest}")
    for name, why in skipped:
        print(f"SKIPPED {name}: {why}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
