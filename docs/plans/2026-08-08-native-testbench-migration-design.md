# Native Testbench Migration — rtlmeter_tests & uhdm_tests

**Date:** 2026-08-08
**Status:** Draft — pending review

## 1. Goal

Replace the cocotb testbenches in `rtlmeter_tests/` and `uhdm_tests/` with the suites' *native* test forms, ported from their upstream repositories, so that every test exercises real logic under RyuSim 2.x's full-SystemVerilog support:

- **rtlmeter_tests** (9 processor designs): today's cocotb TBs are compile/reset/N-cycle smoke tests — the `programs/*.hex` workloads are never executed because no AXI memory model was ever written. After migration, each design runs its upstream SV testbench (`tb_top`/`tb`/`testbench`) executing the full upstream workload set (hello, dhrystone, coremark, boots, kernels) to completion.
- **uhdm_tests** (currently 27 tests): today's cocotb TBs poke DUTs over VPI. After migration, the suite expands to the **full upstream sweep (~363 DUTs)** driven by tiny native SV harnesses generated from the upstream stimulus template, validated by VCD comparison against Verilator.

**Out of scope / unchanged:** `cocotb_tests/` remains native cocotb — those designs *are* cocotb designs, and they retain VPI-backend coverage and the Seiraiyu cocotb fork dependency. The weekly/monthly CI cadence is unchanged.

Why now: RyuSim 1.x supported only synthesizable constructs, forcing cocotb to supply all stimulus (and capping uhdm at the 27 tests that were reasonable to hand-write cocotb TBs for). RyuSim 2.x runs full SystemVerilog testbenches — `initial`, `#` delays, `$readmemh`, `fork`/`join`, `$display`/`$finish`/`$fatal`, DPI — as demonstrated by RyuSimAlt's Taxi suite, which runs native full-SV testbenches in production CI.

## 2. Constraints & principles

1. **Port, don't author.** Test content comes from the existing upstream repos at pinned revisions. We do not invent new tests. The only generated code is the uhdm SV harness, which mechanically reproduces the stimulus schedule of upstream's shared Verilator `main.cpp` template.
2. **Native cocotb designs stay cocotb.** Only content originally lifted from non-cocotb upstreams migrates.
3. **One execution path per suite.** The old cocotb TBs in migrated suites are deleted, not kept alongside. VPI coverage lives in `cocotb_tests/`.
4. **Existing runner CLIs are preserved.** `run_benchmarks.py` / `run_tests.py` keep their flags and output formats; only the invocation under the hood changes.
5. **Existing CI cadence is preserved.** Weekly Validation (8-distro matrix) and Monthly Full Benchmarks keep their triggers; tiering maps onto them.

## 3. Upstream sources (verified)

| Suite | Upstream | Native test form |
|---|---|---|
| rtlmeter_tests | [verilator/rtlmeter](https://github.com/verilator/rtlmeter) `designs/<name>/` | SV testbench in the compile list (`topModule: tb_top`/`tb`/`testbench`), per-test workload files + plusargs in `descriptor.yaml`, pass criteria in `tests/post.bash` (e.g. `grep TEST_PASSED stdout.log`). Vortex additionally has `cppSourceFiles: src/dpi/memory.cpp` (DPI-C memory model). |
| uhdm_tests | [chipsalliance/UHDM-integration-tests](https://github.com/chipsalliance/UHDM-integration-tests) `tests/<name>/` | **No SV testbenches upstream.** Each test is a bare DUT (`top.sv`/`dut.v`) plus a Verilator C++ `main.cpp` harness — 169 of 318 are byte-identical copies of one template (toggle inputs on a fixed schedule, run ~100 cycles, dump VCD, print signals); correctness is `vcddiff` between two build paths. |

Each in-tree design already pins its upstream `repository` + `revision` in `config.yaml` (mirroring rtlmeter's `descriptor.yaml` `origin:`); ports happen at those pinned revisions. New uhdm tests pin the UHDM-integration-tests revision used for the sweep.

## 4. Design — rtlmeter_tests

### 4.1 Per-design layout (after)

```
rtlmeter_tests/VeeR-EL2/
├── rtl/            # DUT sources (unchanged)
├── tb/             # NEW: upstream testbench sources (tb_top.sv, tb_top_pkg.sv, DPI .cpp for Vortex)
├── programs/       # workload hex/elf files — completed to the full upstream set
├── Makefile        # ryusim compile + run targets (cocotb removed)
├── config.yaml     # extended: per-test args/tags/marker (see 4.3)
└── LICENSE*        # upstream licenses (ported alongside any new sources)
```

`cocotb/` directories are deleted. VeeR-EH2's `rtl/tb_top.sv` (already in-tree but excluded) moves to `tb/`.

### 4.2 Build & run

```makefile
# Makefile pattern (native)
compile:
	ryusim compile $(VERILOG_SOURCES) $(TB_SOURCES) --top $(TB_TOP) $(RYUSIM_ARGS)

test-%: compile
	./obj_dir/build/$(TB_TOP)_sim $(ARGS_$*) | tee run_$*.log
	grep -q "$(PASS_MARKER)" run_$*.log
```

- Workload selection follows upstream: program files are copied/symlinked to the names the TB `$readmemh`s (rtlmeter's `execute.tests.<t>.files`), plusargs come from `execute.tests.<t>.args` (e.g. `+iterations=14`).
- Vortex compiles its DPI `memory.cpp` via RyuSim's DPI support; if RyuSim's DPI build flow needs flags, they live in `RYUSIM_ARGS` in that design's Makefile only.
- `--vpi-depth` flags are dropped (no VPI consumer).

### 4.3 Pass/fail contract

A test passes iff **both**:
1. the simulation exits 0 (`$fatal`/`$error` produce nonzero; RyuSim 2.x terminates on `$fatal`), and
2. the per-design **pass marker** appears on stdout (guards against early clean exit that never reached the checks).

`config.yaml` grows, mirroring upstream's descriptor + post.bash:

```yaml
tb:
  top: tb_top
  sources: [tb/tb_top_pkg.sv, tb/tb_top.sv]
pass_marker: "TEST_PASSED"        # from upstream post.bash
tests:
  hello:      { files: [programs/hello.hex],  tags: [sanity] }
  dhrystone:  { files: [programs/dhry.hex],   args: ["+iterations=17500"], tags: [standard] }
  coremark:   { files: [programs/cmark.hex],  args: ["+iterations=14"],    tags: [standard] }
```

### 4.4 Workload bar

**Full workloads everywhere**: every design ports its complete upstream workload set (all `execute.tests` entries for the configurations we carry). VeeR programs are already in-tree; XuanTie/BlackParrot/Vortex workloads are ported from upstream `tests/` dirs at the pinned revisions.

### 4.5 Verilator comparison

`run_benchmarks.py --compare-verilator` builds the *same* `tb/` + `rtl/` under Verilator (using upstream's `verilatorArgs` where relevant) and compares wall-clock — for the first time a true apples-to-apples benchmark, since both simulators execute the identical testbench and workload.

## 5. Design — uhdm_tests

### 5.1 Per-test layout (after)

```
uhdm_tests/<category>/<subcat>/<name>/
├── dut.sv          # upstream DUT, unmodified
├── tb.sv           # generated SV harness (see 5.2)
├── golden.vcd      # committed Verilator golden (see 5.3)
├── Makefile        # compile + run + vcddiff targets
└── config.yaml     # name/category/ieee_section/level/skip-status
```

The existing 27 tests are re-based onto their upstream DUTs; the sweep adds the remaining upstream tests. The current 5-category taxonomy (`combinational/sequential/hierarchy/advanced/unsupported`) is preserved for organization; new tests are slotted during triage.

### 5.2 Generated SV harness

A committed generator (`tools/gen_uhdm_harness.py`) emits `tb.sv` per test:

- **Template tests** (169+ sharing upstream's byte-identical `main.cpp`): the harness reproduces that template's exact stimulus schedule in an `initial` block — same input-toggle cadence, same ~100-cycle horizon, `$dumpvars`-equivalent tracing via `--trace-vcd`, `$finish` at the horizon. Port mapping is derived from the DUT's declared ports.
- **Custom tests** (the remaining `main.cpp` variants, in template-sized clusters of ≤16): each cluster's stimulus is ported once, faithfully, into a variant template. These are stimulus ports, not new tests.
- Generated harnesses are committed (reviewable, diffable); the generator is rerun only when a DUT or template changes.

The same `tb.sv` compiles under both RyuSim and Verilator — improving on upstream, which compared two Verilator builds of *different* front-end paths.

### 5.3 Validation levels & goldens

- **Level 1:** `ryusim compile` exits 0 and the harness runs to `$finish` with exit 0.
- **Level 2:** RyuSim's VCD matches the committed `golden.vcd` via `vcddiff`.

Goldens are **committed to the repo**: `tools/regen_goldens.py` builds each `tb.sv`+DUT under Verilator and writes `golden.vcd` (tiny — ~100 cycles of small DUTs). CI legs never install Verilator for uhdm; they run RyuSim + `vcddiff` only. A staleness guard (hash of `dut.sv`+`tb.sv` recorded next to each golden, checked by `run_tests.py`) fails a test whose golden predates its sources, prompting regeneration.

### 5.4 Sweep triage, skip/xfail, and expect-fail

Porting ~363 DUTs will surface tests that RyuSim or Verilator reject. Triage produces an explicit, reasoned status in each `config.yaml`:

- `status: active` — normal test (default).
- `status: skip, reason: "..."` — not runnable under this flow (e.g. Verilator-specific constructs, yosys-only tests); excluded with the reason surfaced in runner output so skips are never silent.
- `status: xfail, reason: "...", expect: "diagnostic substring"` — RyuSim 2.x genuinely rejects the construct; the test passes when compilation fails **with a clean diagnostic** matching `expect`.

The old `unsupported/` category (1.x-era: `initial`, `fork`/`join`, classes, `$display`) **flips to positive tests** — those constructs are exactly what 2.x now supports and this suite must prove. The new expect-fail set is *derived from triage data*, not assumed up front.

## 6. Runners

### 6.1 `run_benchmarks.py`

- Keeps `--all / --design / --test / --compare-verilator / --output` and the JSON result schema (fields for compile time, run time, pass/fail, stdout tail).
- Gains `--tags sanity|standard` filtering (used by CI; default = all).
- Invocation changes from `make` (cocotb) to the design's native `make test-<name>` targets; pass/fail per §4.3.

### 6.2 `run_tests.py`

- Keeps `--all / --category / --test / --level / --output`.
- Level 1/2 semantics per §5.3; honors `status:` skip/xfail; reports skip reasons in output.
- `--category unsupported` continues to work during transition, backed by the new xfail mechanism.

## 7. CI

Existing workflows keep their triggers; steps change:

| Workflow | Cadence | After migration |
|---|---|---|
| `nightly.yml` (Weekly Validation) | Mon cron, 8 distros | cocotb_tests (cocotb) + rtlmeter `--tags sanity` + uhdm level 1 |
| `monthly-benchmarks.yml` | 1st-of-month cron | full rtlmeter workloads (`standard`) + uhdm level 2 |
| `benchmarks.yml`, `sv-tests.yml` | dispatch/push | same reshaping; sv-tests adds the golden staleness guard |

cocotb/pip installs remain only where cocotb_tests runs. Timeouts for `standard` workloads come from each design's `config.yaml` `timeout`, raised per upstream runtimes.

## 8. Error handling & failure modes

- **Simulation hang:** per-test timeout (config.yaml) enforced by the runner; timeout = fail with `timeout` status, never ambiguous.
- **Marker absent but exit 0:** fail (`marker-missing`) — distinguishes "ran but never validated" from crash.
- **vcddiff mismatch:** fail with the vcddiff output captured in the JSON result.
- **Stale golden:** distinct `stale-golden` failure, pointing at `tools/regen_goldens.py`.
- **RyuSim regressions found by native TBs** (new constructs now on the execution path): that is this repo's job — failures are reported as validation findings against RyuSim, filed upstream, and may be temporarily `xfail`ed with an issue link, never silently skipped.

## 9. Testing approach for the migration itself

Each phase lands green before the next starts:

1. Prove the toolchain end-to-end on **VeeR-EL2** first (upstream TB + in-tree hex programs already available): compile `tb_top` under RyuSim, run hello → TEST_PASSED, then dhrystone/coremark.
2. Every migrated design must pass its `sanity` workload locally and in the weekly matrix before its cocotb TB is deleted (delete happens in the same PR that lands the working native TB — no coverage gap, no long dual-track).
3. uhdm: generator + goldens land with the 27 re-based tests first (validating the form), then the sweep in category-sized batches with triage notes.
4. Docs (`CLAUDE.md`, `README.md`) update in the final phase — constraint sections rewritten for 2.x (native TBs supported; cocotb required only for `cocotb_tests/`).

## 10. Phases

| Phase | Description | Status | Tested | Pushed |
|-------|-------------|--------|--------|--------|
| 1 | Runner + Makefile native-mode plumbing; VeeR-EL2 ported end-to-end (hello/dhry/cmark TEST_PASSED) | pending | no | no |
| 2 | VeeR-EH1, VeeR-EH2 ported, full workloads; cocotb TBs deleted per-design | pending | no | no |
| 3 | XuanTie E902/E906/C906/C910 ported, full workloads | pending | no | no |
| 4 | BlackParrot + Vortex (DPI) ported, full workloads | pending | no | no |
| 5 | uhdm harness generator + goldens pipeline; 27 existing tests re-based | pending | no | no |
| 6 | uhdm full upstream sweep w/ triage (skip/xfail lists, expect-fail rebuilt from 2.x reality) | pending | no | no |
| 7 | CI workflows reshaped (tags/levels), staleness guard; docs rewritten; final cocotb removal from migrated suites | pending | no | no |

## 11. Decisions log (from design interview, 2026-08-08)

| Decision | Choice |
|---|---|
| Scope | rtlmeter + uhdm migrate; cocotb_tests stays cocotb |
| Old cocotb TBs in migrated suites | Deleted (per-design, same PR as working native TB) |
| Pass/fail | Exit code 0 **and** pass marker on stdout |
| Workload bar | Full upstream workloads for all 9 designs |
| Test provenance | Port existing upstream tests only; no newly-authored tests |
| uhdm harness form | Generated SV harness reproducing upstream main.cpp stimulus; vcddiff vs Verilator |
| uhdm scope | Full upstream sweep (~363), not just the in-tree 27 |
| Expect-fail | Rebuilt from what 2.x actually rejects (triage-driven) |
| Golden VCDs | Committed to repo; regeneration script + staleness guard |
| CI tiering | Existing weekly/monthly split; sanity weekly, standard monthly |

## 12. Risks

- **RyuSim 2.x gaps** (e.g. XuanTie TBs' vendor-specific system tasks, BlackParrot's DPI-heavy basejump harness) may block a design; mitigated by per-design phasing — one stuck design doesn't block the rest — and by xfail-with-issue rather than silent skip.
- **Sweep triage volume** (~363 DUTs) is the largest unknown; mitigated by batching per category and by the skip/xfail mechanism making partial progress shippable.
- **Golden drift** if contributors edit DUTs without regenerating; mitigated by the staleness guard failing loudly.
- **Benchmark runtimes** under monthly CI may exceed current timeouts; timeouts are re-derived from upstream rtlmeter runtimes during each design's port.
