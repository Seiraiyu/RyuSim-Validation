# Native Testbench Migration — Phase 1 Implementation Plan

**Goal:** Prove the native-testbench toolchain end-to-end: VeeR-EL2 runs its upstream rtlmeter `tb_top` under RyuSim standalone, executing hello/dhrystone/coremark/coremark_iccm to `TEST_PASSED`, with `run_benchmarks.py` gaining native-mode + `--tags` support.

**Architecture:** The design's cocotb smoke TB is replaced by upstream rtlmeter's `tb_top.sv` (vendored at a pinned rtlmeter revision into `tb/`). The Makefile compiles DUT+TB with `ryusim compile --top tb_top` and runs the standalone `tb_top_sim` binary per test in a staged work dir (`program.hex` + plusargs). Pass = exit 0 AND `TEST_PASSED` on stdout. `run_benchmarks.py` detects native designs via a `tb:` key in `config.yaml` and runs per-test make targets; cocotb designs are untouched.

**Tech Stack:** RyuSim 2.0.4 (installed binary), GNU make, Python 3.10+ (pyyaml), upstream [verilator/rtlmeter](https://github.com/verilator/rtlmeter) @ `a9180d6c55d2bf02ee574a8f60f614a85050b91c`.

**Design doc:** `docs/plans/2026-08-08-native-testbench-migration-design.md` (approved). This plan covers **Phase 1 only**; Phases 2–7 get their own plans informed by what this phase verifies.

**Known-unverified assumptions** (Task 1/6 confirm and adjust):
- `ryusim compile` flag spellings for include dirs (`-I…`) and parallel build (`--jobs`). `--top` and `--jobs` are confirmed by the repo's existing Makefiles; the CLI ships `include_option`, `plusargs_option`, `top_option` headers, so the features exist even if a spelling differs.
- Standalone binary path `obj_dir/build/tb_top_sim` (CLAUDE.md documents `module_sim`; RyuSimAlt docs show `./obj_dir/build/top_sim +ryusim_seed=N`, confirming plusargs pass-through).
- Phase 1 uses the **default** VeeR configuration only; hiperf/asic configurations are a later phase.

| Task | Description | Status | Tested | Pushed |
|------|-------------|--------|--------|--------|
| 1 | Install RyuSim, capture CLI reality | pending | no | no |
| 2 | Vendor upstream tb_top into `tb/` | pending | no | no |
| 3 | Verify DUT/program parity vs upstream | pending | no | no |
| 4 | Rewrite VeeR-EL2 Makefile (native) | pending | no | no |
| 5 | Extend VeeR-EL2 config.yaml | pending | no | no |
| 6 | `make compile` green | pending | no | no |
| 7 | `make test-hello` → TEST_PASSED; commit design port | pending | no | no |
| 8 | run_benchmarks.py native mode + `--tags` | pending | no | no |
| 9 | Runner verified on VeeR-EL2 hello; commit runner | pending | no | no |
| 10 | Full workloads green (dhry/cmark/cmark_iccm) | pending | no | no |
| 11 | Delete cocotb TB + veer_wrapper; re-verify; commit | pending | no | no |
| 12 | `--tags` verified; phase table updated; final commit | pending | no | no |

---

### Task 1: Install RyuSim, capture CLI reality

**Files:** none (environment)

**Step 1: Install**
```bash
curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash
export PATH="$PATH:/opt/ryusim/bin"   # or path the installer prints
ryusim --version
```
Expected: version string containing `2.0.4`.

**Step 2: Capture compile flags**
```bash
ryusim compile --help | tee /tmp/ryusim-compile-help.txt
```
Confirm the exact spellings for: top module (`--top`), include directory, parallel jobs, output dir. **If any flag below differs from this help output, use the help output's spelling in Tasks 4/6.**

---

### Task 2: Vendor upstream tb_top into `tb/`

**Files:**
- Create: `rtlmeter_tests/VeeR-EL2/tb/tb_top.sv`
- Create: `rtlmeter_tests/VeeR-EL2/tb/tb_top_pkg.sv`

**Step 1: Fetch rtlmeter at the pinned revision**
```bash
cd /tmp && rm -rf rtlmeter-pin && git clone --no-checkout https://github.com/verilator/rtlmeter.git rtlmeter-pin
cd rtlmeter-pin && git checkout a9180d6c55d2bf02ee574a8f60f614a85050b91c -- designs/VeeR-EL2
```

**Step 2: Copy TB sources (unmodified)**
```bash
mkdir -p ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2/tb
cp /tmp/rtlmeter-pin/designs/VeeR-EL2/src/tb_top.sv \
   /tmp/rtlmeter-pin/designs/VeeR-EL2/src/tb_top_pkg.sv \
   ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2/tb/
```

**Step 3: Verify**
```bash
grep -c 'TEST_PASSED' ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2/tb/tb_top.sv
```
Expected: `1` (the `$display("TEST_PASSED")` at the mailbox handler).

No commit yet (commits with Task 7 once the port runs).

---

### Task 3: Verify DUT/program parity vs upstream

**Files:** none (verification only; fix-forward if mismatched)

**Step 1: Program hex parity** (already verified once during design, re-verify for the record)
```bash
cd ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2
md5sum programs/hello.hex programs/dhrystone.hex programs/coremark.hex programs/coremark_iccm.hex
md5sum /tmp/rtlmeter-pin/designs/VeeR-EL2/tests/{hello,dhry,cmark,cmark_iccm}/program.hex
```
Expected pairs (in-tree ↔ upstream): hello `dc127d5c…`, dhrystone/dhry `496af20a…`, coremark/cmark `180fd11b…`, coremark_iccm/cmark_iccm `f3ab51c0…`. All four already match — any mismatch means the vendor step grabbed the wrong revision; stop and re-check Task 2.

**Step 2: DUT source parity**
```bash
for f in /tmp/rtlmeter-pin/designs/VeeR-EL2/src/*.sv /tmp/rtlmeter-pin/designs/VeeR-EL2/src/*.v; do
  b=$(basename "$f"); [ "$b" = tb_top.sv ] || [ "$b" = tb_top_pkg.sv ] && continue
  diff -q "$f" "rtl/$b" || echo "MISMATCH: $b"
done
```
Expected: no `MISMATCH` lines (in-tree `rtl/` was ported from the same VeeR revision `c5c00458…`). If a file differs, copy the upstream version into `rtl/` and note it in the Task 7 commit message.

---

### Task 4: Rewrite VeeR-EL2 Makefile (native)

**Files:**
- Modify: `rtlmeter_tests/VeeR-EL2/Makefile` (full replacement)

**Step 1: Write the Makefile**
```makefile
# VeeR-EL2 — native testbench (upstream rtlmeter tb_top) under RyuSim.
#
# tb_top $readmemh's "program.hex" from the cwd, so each test runs in
# work/<test>/ with its program staged; iteration counts come from upstream
# rtlmeter descriptor.yaml (default configuration).
SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

TB_TOP = tb_top
SIM_BIN = obj_dir/build/$(TB_TOP)_sim
PASS_MARKER = TEST_PASSED

# Upstream descriptor.yaml compile order (src/ -> rtl/), TB last.
RTL_SOURCES = \
    rtl/el2_def.sv \
    rtl/el2_veer_wrapper.sv \
    rtl/el2_mem.sv \
    rtl/el2_pic_ctrl.sv \
    rtl/el2_veer.sv \
    rtl/el2_dma_ctrl.sv \
    rtl/el2_pmp.sv \
    rtl/el2_ifu_aln_ctl.sv \
    rtl/el2_ifu_compress_ctl.sv \
    rtl/el2_ifu_ifc_ctl.sv \
    rtl/el2_ifu_bp_ctl.sv \
    rtl/el2_ifu_ic_mem.sv \
    rtl/el2_ifu_mem_ctl.sv \
    rtl/el2_ifu_iccm_mem.sv \
    rtl/el2_ifu.sv \
    rtl/el2_dec_decode_ctl.sv \
    rtl/el2_dec_gpr_ctl.sv \
    rtl/el2_dec_ib_ctl.sv \
    rtl/el2_dec_pmp_ctl.sv \
    rtl/el2_dec_tlu_ctl.sv \
    rtl/el2_dec_trigger.sv \
    rtl/el2_dec.sv \
    rtl/el2_exu_alu_ctl.sv \
    rtl/el2_exu_mul_ctl.sv \
    rtl/el2_exu_div_ctl.sv \
    rtl/el2_exu.sv \
    rtl/el2_lsu.sv \
    rtl/el2_lsu_clkdomain.sv \
    rtl/el2_lsu_addrcheck.sv \
    rtl/el2_lsu_lsc_ctl.sv \
    rtl/el2_lsu_stbuf.sv \
    rtl/el2_lsu_bus_buffer.sv \
    rtl/el2_lsu_bus_intf.sv \
    rtl/el2_lsu_ecc.sv \
    rtl/el2_lsu_dccm_mem.sv \
    rtl/el2_lsu_dccm_ctl.sv \
    rtl/el2_lsu_trigger.sv \
    rtl/el2_dbg.sv \
    rtl/dmi_mux.v \
    rtl/dmi_wrapper.v \
    rtl/dmi_jtag_to_core_sync.v \
    rtl/rvjtag_tap.v \
    rtl/el2_lib.sv \
    rtl/beh_lib.sv \
    rtl/mem_lib.sv \
    rtl/axi_lsu_dma_bridge.sv \
    rtl/ahb_sif.sv \
    rtl/el2_mem_if.sv

TB_SOURCES = tb/tb_top_pkg.sv tb/tb_top.sv

# Flag spellings verified against `ryusim compile --help` in Task 1.
RYUSIM_FLAGS = --top $(TB_TOP) -Irtl -Irtl/default --jobs 4

# Per-test plusargs — upstream descriptor.yaml, default configuration.
ARGS_hello =
ARGS_dhrystone = +iterations=17500
ARGS_coremark = +iterations=14
ARGS_coremark_iccm = +iterations=22

PROGRAM_hello = hello.hex
PROGRAM_dhrystone = dhrystone.hex
PROGRAM_coremark = coremark.hex
PROGRAM_coremark_iccm = coremark_iccm.hex

compile: $(SIM_BIN)

$(SIM_BIN): $(RTL_SOURCES) $(TB_SOURCES)
	ryusim compile $(RTL_SOURCES) $(TB_SOURCES) $(RYUSIM_FLAGS)

test-%: compile
	mkdir -p work/$*
	cp programs/$(PROGRAM_$*) work/$*/program.hex
	cd work/$* && ../../$(SIM_BIN) $(ARGS_$*) 2>&1 | tee run.log
	grep -q "$(PASS_MARKER)" work/$*/run.log

all: test-hello test-dhrystone test-coremark test-coremark_iccm

clean:
	rm -rf obj_dir work

.PHONY: compile all clean
.DEFAULT_GOAL := all
```
Note: `rtl/veer_wrapper.sv` (the cocotb port-flattening wrapper) is intentionally absent — upstream's list doesn't contain it; it is deleted in Task 11.

**Step 2: Syntax check**
```bash
cd ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2 && make -n compile | head -3
```
Expected: the echoed `ryusim compile …` command, no make errors.

---

### Task 5: Extend VeeR-EL2 config.yaml

**Files:**
- Modify: `rtlmeter_tests/VeeR-EL2/config.yaml` (full replacement)

**Step 1: Write**
```yaml
name: VeeR-EL2
source: rtlmeter
tier: 1
description: "Western Digital VeeR EL2 — production RISC-V RV32IMC core (CHIPS Alliance)"
top_module: tb_top
timeout: 1800
upstream:
  repository: https://github.com/chipsalliance/Cores-VeeR-EL2.git
  revision: c5c004589ee0a308b63278ee609e1597f61a4143
  license: Apache-2.0
tb_upstream:
  repository: https://github.com/verilator/rtlmeter.git
  revision: a9180d6c55d2bf02ee574a8f60f614a85050b91c
  files:
    - designs/VeeR-EL2/src/tb_top.sv
    - designs/VeeR-EL2/src/tb_top_pkg.sv
tb:
  top: tb_top
  sources:
    - tb/tb_top_pkg.sv
    - tb/tb_top.sv
pass_marker: "TEST_PASSED"
configurations:
  default:
    include_dirs:
      - rtl/default
  hiperf:
    include_dirs:
      - rtl/hiperf
  asic:
    include_dirs:
      - rtl/asic
tests:
  hello:
    program: programs/hello.hex
    tags: [sanity]
    description: "Hello World — basic sanity test"
  dhrystone:
    program: programs/dhrystone.hex
    args: ["+iterations=17500"]
    tags: [standard]
    description: "Dhrystone benchmark"
  coremark:
    program: programs/coremark.hex
    args: ["+iterations=14"]
    tags: [standard]
    description: "CoreMark benchmark"
  coremark_iccm:
    program: programs/coremark_iccm.hex
    args: ["+iterations=22"]
    tags: [standard]
    description: "CoreMark benchmark (ICCM execution)"
```

**Step 2: Validate YAML**
```bash
cd ~/RyuSim-Validation && python3 -c "import yaml; c=yaml.safe_load(open('rtlmeter_tests/VeeR-EL2/config.yaml')); print(c['tb']['top'], c['pass_marker'], list(c['tests']))"
```
Expected: `tb_top TEST_PASSED ['hello', 'dhrystone', 'coremark', 'coremark_iccm']`

---

### Task 6: `make compile` green

**Step 1: Compile**
```bash
cd ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2 && time make compile
```
Expected: exit 0; `obj_dir/build/tb_top_sim` exists and is executable. This is the first time RyuSim compiles VeeR's *testbench* (`initial`, `#` delays, `$readmemh`, `$fopen`) — several minutes is normal.

**Troubleshooting (adjust, don't abandon):**
- Unknown flag → re-check `/tmp/ryusim-compile-help.txt` spellings (include dir, jobs) and fix `RYUSIM_FLAGS`.
- Binary at a different path (e.g. `obj_dir/tb_top_sim`) → fix `SIM_BIN` and re-run.
- Compile errors inside `tb_top.sv` → record the exact diagnostic; this is a RyuSim 2.x finding. File it against RyuSimAlt and stop the phase here (the design's §8 covers this: validation findings are the product).

**Step 2: Verify binary**
```bash
ls -la obj_dir/build/tb_top_sim && file obj_dir/build/tb_top_sim
```
Expected: ELF executable.

---

### Task 7: `make test-hello` → TEST_PASSED; commit the port

**Step 1: Run**
```bash
cd ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2 && make test-hello
```
Expected: stdout includes the VeeR console output ending with `TEST_PASSED`; `grep` succeeds; exit 0. Seconds-to-minutes runtime.

**Step 2: Inspect the log**
```bash
tail -20 work/hello/run.log
```
Expected: `Hello World` program console output, `TEST_PASSED`, simulation finish banner.

**Step 3: Commit**
```bash
cd ~/RyuSim-Validation && git add rtlmeter_tests/VeeR-EL2/tb rtlmeter_tests/VeeR-EL2/Makefile rtlmeter_tests/VeeR-EL2/config.yaml && git commit -m "feat(veer-el2): native rtlmeter tb_top under RyuSim standalone — hello TEST_PASSED

Vendors tb_top.sv/tb_top_pkg.sv from verilator/rtlmeter@a9180d6c,
replaces the cocotb Makefile with ryusim compile + standalone run,
pass = exit 0 AND TEST_PASSED marker (design doc §4). Phase 1.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: run_benchmarks.py native mode + `--tags`

**Files:**
- Modify: `run_benchmarks.py`

**Step 1: Add the native runner** — insert after `run_benchmark`'s docstring-bearing definition (i.e. as a new top-level function above `run_benchmark`, `run_benchmarks.py:66`):

```python
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
```

**Step 2: Dispatch native designs** — in `run_benchmark`, immediately after the config is loaded successfully (after the `except FileNotFoundError` block, `run_benchmarks.py:94`), add:

```python
    if "tb" in config:
        return run_native_benchmark(
            design_path, config, test_name=test_name, tags=tags,
            compare_verilator=compare_verilator, timeout_override=timeout_override,
        )
```
and change `run_benchmark`'s signature to `def run_benchmark(design_path, test_name=None, compare_verilator=False, timeout_override=None, tags=None):`

**Step 3: Add `--tags`** — in `main()` next to the other arguments (`run_benchmarks.py:215`):

```python
    parser.add_argument(
        "--tags",
        type=str,
        help="Comma-separated test tags to run (native designs only), e.g. --tags sanity",
    )
```
and thread it through the `run_benchmark` call (`run_benchmarks.py:245`):

```python
        result = run_benchmark(
            design,
            test_name=args.test,
            compare_verilator=args.compare_verilator,
            timeout_override=args.timeout,
            tags=[t.strip() for t in args.tags.split(",")] if args.tags else None,
        )
```

**Step 4: Sanity-import**
```bash
cd ~/RyuSim-Validation && python3 -c "import run_benchmarks" && python3 run_benchmarks.py --help | grep -- --tags
```
Expected: no import error; `--tags` shown in help.

---

### Task 9: Runner verified on VeeR-EL2 hello; commit runner

**Step 1: Run one native test through the runner**
```bash
cd ~/RyuSim-Validation && python3 run_benchmarks.py --design VeeR-EL2 --test hello --verbose
```
Expected: JSON summary with `"passed": 1`, the VeeR-EL2 result having `"mode": "native"`, a `tests` list with `hello: passed`, and exit code 0.

**Step 2: Confirm cocotb designs are untouched**
```bash
python3 run_benchmarks.py --design Example --source cocotb --verbose
```
Expected: runs exactly as before this change (legacy make path; result has no `"mode"` key).

**Step 3: Commit**
```bash
git add run_benchmarks.py && git commit -m "feat(runner): native-testbench mode + --tags in run_benchmarks.py

Designs whose config.yaml has a tb: key run make compile + per-test
make test-<name>; per-test results and tag filtering added. cocotb
designs unchanged. Phase 1.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 10: Full workloads green

**Step 1: Dhrystone**
```bash
cd ~/RyuSim-Validation/rtlmeter_tests/VeeR-EL2 && time make test-dhrystone
```
Expected: `TEST_PASSED`, exit 0. Note the wall time.

**Step 2: CoreMark + CoreMark-ICCM**
```bash
time make test-coremark && time make test-coremark_iccm
```
Expected: `TEST_PASSED` for both.

**Step 3: If any run exceeds ~25 min**, raise `timeout:` in `config.yaml` to 2× the observed time and note it for the CI phase. Commit only if changed:
```bash
cd ~/RyuSim-Validation && git add rtlmeter_tests/VeeR-EL2/config.yaml && git commit -m "chore(veer-el2): timeout raised to observed native workload runtime

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 11: Delete cocotb TB + veer_wrapper; re-verify; commit

**Files:**
- Delete: `rtlmeter_tests/VeeR-EL2/cocotb/` (whole dir)
- Delete: `rtlmeter_tests/VeeR-EL2/rtl/veer_wrapper.sv` (cocotb-only flattening wrapper; not in upstream's source list)

**Step 1: Delete**
```bash
cd ~/RyuSim-Validation && git rm -r rtlmeter_tests/VeeR-EL2/cocotb && git rm rtlmeter_tests/VeeR-EL2/rtl/veer_wrapper.sv
```

**Step 2: Full clean rebuild + all tests via the runner**
```bash
cd rtlmeter_tests/VeeR-EL2 && make clean && cd ~/RyuSim-Validation
python3 run_benchmarks.py --design VeeR-EL2 --verbose
```
Expected: all 4 tests `passed`, exit 0.

**Step 3: Commit**
```bash
git commit -m "refactor(veer-el2): remove cocotb testbench and flattening wrapper

Native tb_top fully replaces the cocotb smoke tests (design doc §2.3:
delete in the same change that lands the working native TB).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 12: `--tags` verified; phase table updated; final commit

**Step 1: Tag filtering**
```bash
cd ~/RyuSim-Validation && python3 run_benchmarks.py --design VeeR-EL2 --tags sanity --verbose
```
Expected: only `hello` in the result's `tests` list, `passed`, exit 0.

**Step 2: Update both tracking tables**
- This file: mark Tasks 1–12 `done / yes`.
- `docs/plans/2026-08-08-native-testbench-migration-design.md` §10: Phase 1 → `done | yes | yes`.

**Step 3: Final commit + push**
```bash
git add docs/plans/2026-08-08-native-tb-phase1-plan.md docs/plans/2026-08-08-native-testbench-migration-design.md
git commit -m "docs(plans): Phase 1 complete — VeeR-EL2 native tb_top end-to-end under RyuSim

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git push
```

---

## After Phase 1

Phase 2 (VeeR-EH1/EH2) gets its own plan using the now-verified recipe: vendor `tb/` at the rtlmeter pin, mirror the descriptor source list and plusargs, extend config.yaml, run, delete cocotb. Findings from Task 6/7 (actual flag spellings, sim binary path, runtimes) feed directly into it.
