# RyuSim SystemVerilog Construct Coverage Tests

**Date:** 2025-12-15 (original), 2026-02-02 (revised)
**Status:** Planned
**Repo:** `Seiraiyu/ryusim-sv-tests` (standalone)

> **Revision note:** Originally designed around porting the UHDM-integration-tests repo (Surelog/UHDM pipeline). Rewritten for RyuSim's actual architecture (Slang frontend) and as a standalone repo consuming released RyuSim binaries.

## Overview

A standalone test suite that validates RyuSim's SystemVerilog construct coverage. Each test is a minimal `.sv` file exercising a specific language construct, compiled and run via the released `ryusim` binary.

### Goals

1. Exhaustive coverage of IEEE 1800-2023 synthesizable constructs
2. Two validation levels:
   - **Level 1:** Pipeline completion (`ryusim compile` exits 0, simulation runs)
   - **Level 2:** Functional correctness (VCD comparison against Verilator golden references)
3. Regression suite for catching construct support regressions across releases
4. Clear documentation of what RyuSim supports and what it intentionally does not

### What This Is NOT

This is not a benchmark suite (that's `ryusim-benchmarks`). These are small, focused tests — typically 5-50 lines of SV each — designed to exercise individual language constructs in isolation.

---

## RyuSim Installation

```bash
# Install latest release
curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash

# Or pin a specific version
RYUSIM_VERSION=1.0.0 curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash
```

---

## Test Categories

All tests target **synthesizable SystemVerilog only** — matching RyuSim's design scope.

### Category 1: Combinational Logic (~120 tests)

Pure `assign` and `always_comb` constructs.

| Subcategory | Examples | Est. Count |
|-------------|----------|------------|
| Operators | Arithmetic, bitwise, logical, shift, reduction | 20 |
| Ternary / conditional | Nested ternary, inside operator | 8 |
| Part-selects | Constant, indexed, variable | 10 |
| Concatenation | Concat, replication, streaming | 8 |
| Type casting | Signed/unsigned, width casting | 10 |
| Arrays | Packed, unpacked, multi-dim, array slicing | 15 |
| Structs | Packed struct, nested struct, struct assignment | 10 |
| Unions | Packed union, tagged union | 6 |
| Enums | Enum declaration, methods, casting | 8 |
| Functions | Combinational functions, automatic functions | 10 |
| Generate | For-generate, if-generate, case-generate | 10 |
| Parameters | Parameter, localparam, parameter override | 8 |
| Interfaces | Interface ports, modports, virtual interfaces | 7 |

### Category 2: Sequential Logic (~60 tests)

`always_ff` and `always_latch` constructs.

| Subcategory | Examples | Est. Count |
|-------------|----------|------------|
| Basic flops | D-FF, enabled FF, reset (sync/async) | 8 |
| Counters | Up, down, loadable, gray code | 6 |
| Shift registers | SISO, SIPO, PISO, LFSR | 6 |
| FSMs | One-hot, binary, gray, Mealy, Moore | 10 |
| Memories | Register file, ROM, dual-port RAM | 6 |
| Clock domain | Multi-clock, clock gating | 4 |
| Latches | always_latch, transparent latch | 4 |
| Reset patterns | Sync reset, async reset, active-low | 6 |
| Pipelines | Pipeline stages, pipeline flush | 5 |
| Edge cases | Blocking in always_ff (lint check), sensitivity | 5 |

### Category 3: Hierarchy & Elaboration (~40 tests)

Module instantiation, parameterization, and elaboration.

| Subcategory | Examples | Est. Count |
|-------------|----------|------------|
| Module instantiation | Named ports, positional, wildcard | 6 |
| Parameter override | defparam, #() override, type parameters | 8 |
| Generate blocks | Conditional, loop, nested generate | 8 |
| Packages | Package import, wildcard import, export | 6 |
| Interfaces | Interface instantiation, modport connection | 6 |
| Hierarchy depth | 3+ levels of nesting | 3 |
| Multi-file | Cross-file module references | 3 |

### Category 4: Advanced Constructs (~30 tests)

Less common but valid synthesizable constructs.

| Subcategory | Examples | Est. Count |
|-------------|----------|------------|
| SystemVerilog types | shortint, longint, byte, bit, string param | 6 |
| Type definitions | typedef, typedef enum, typedef struct | 6 |
| Assertions | Immediate assertions (synthesis subset) | 4 |
| Attributes | synthesis attributes, pragma | 3 |
| `always @*` | Legacy sensitivity | 3 |
| Multi-driven nets | tri, wand, wor | 4 |
| Wildcard | `.*` port connection | 2 |
| Let / bind | Let declarations | 2 |

### Category 5: Intentionally Unsupported (~30 tests, expect-fail)

Tests that should fail gracefully with a clear error message.

| Construct | Why Unsupported |
|-----------|----------------|
| `initial begin` | Non-synthesizable (use reset logic) |
| `#` delays | Non-synthesizable |
| `fork`/`join` | Non-synthesizable |
| Classes | Non-synthesizable |
| Mailboxes, semaphores | Non-synthesizable |
| `$display`, `$finish` | Testbench constructs (use cocotb) |
| Randomization | Non-synthesizable |
| Dynamic arrays | Non-synthesizable |
| Program blocks | Non-synthesizable |

These tests validate that RyuSim produces a meaningful error, not a crash or silent miscompilation.

---

## Repository Structure

```
ryusim-sv-tests/
├── README.md
├── requirements.txt               # Python deps (cocotb, pytest)
├── setup_ryusim.sh                # Download + install ryusim release
├── run_tests.py                   # Test runner
├── test_manifest.json             # All tests with metadata
├── conftest.py                    # pytest fixtures
│
├── .github/
│   └── workflows/
│       ├── test.yml               # Run on push + manual trigger
│       └── nightly.yml            # Nightly against latest release
│
├── tests/
│   ├── combinational/             # Category 1
│   │   ├── operators/
│   │   │   ├── add_sub/
│   │   │   │   ├── dut.sv
│   │   │   │   ├── test_add_sub.py    # cocotb test
│   │   │   │   └── Makefile
│   │   │   ├── bitwise/
│   │   │   │   ├── dut.sv
│   │   │   │   ├── test_bitwise.py
│   │   │   │   └── Makefile
│   │   │   └── .../
│   │   ├── arrays/
│   │   ├── structs/
│   │   └── .../
│   │
│   ├── sequential/                # Category 2
│   │   ├── basic_flops/
│   │   ├── fsm/
│   │   ├── memories/
│   │   └── .../
│   │
│   ├── hierarchy/                 # Category 3
│   │   ├── module_instantiation/
│   │   ├── parameters/
│   │   └── .../
│   │
│   ├── advanced/                  # Category 4
│   │   ├── typedefs/
│   │   ├── assertions/
│   │   └── .../
│   │
│   └── unsupported/               # Category 5 (expect-fail)
│       ├── initial_block/
│       │   ├── dut.sv
│       │   └── expected_error.txt
│       ├── fork_join/
│       └── .../
│
├── golden/                        # Verilator golden VCDs (Level 2)
│   ├── sequential/
│   │   ├── basic_flops/d_ff.vcd
│   │   └── .../
│   └── .../
│
└── results/                       # Test results (gitignored)
    ├── v1.0.0.json
    └── latest.json
```

---

## Test Format

### Level 1 Test (pipeline completion)

Each test is a directory with:

**dut.sv** — Minimal SV design:
```systemverilog
module add_sub (
    input  logic [7:0] a, b,
    input  logic       op,  // 0=add, 1=sub
    output logic [8:0] result
);
    assign result = op ? (a - b) : (a + b);
endmodule
```

**test_add_sub.py** — cocotb testbench:
```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_add(dut):
    dut.a.value = 10
    dut.b.value = 20
    dut.op.value = 0
    await Timer(1, units="ns")
    assert dut.result.value == 30

@cocotb.test()
async def test_sub(dut):
    dut.a.value = 30
    dut.b.value = 10
    dut.op.value = 1
    await Timer(1, units="ns")
    assert dut.result.value == 20
```

**Makefile**:
```makefile
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = dut.sv
TOPLEVEL = add_sub
MODULE = test_add_sub

include $(shell cocotb-config --makefiles)/Makefile.sim
```

### Level 2 Test (VCD comparison)

Same as Level 1, but adds `--trace-vcd` and compares output against a golden VCD:

```bash
# Generate golden (one-time, using Verilator)
SIM=verilator make
cp sim_build/dump.vcd ../../golden/combinational/operators/add_sub.vcd

# Run RyuSim and compare
SIM=ryusim make
vcddiff golden/combinational/operators/add_sub.vcd sim_build/dump.vcd
```

### Expect-Fail Test (unsupported constructs)

**dut.sv**:
```systemverilog
module bad_initial (output logic [7:0] o);
    initial begin
        o = 8'hFF;
    end
endmodule
```

**expected_error.txt**:
```
initial
```

The test runner verifies that `ryusim compile` exits non-zero and the error message contains the expected keyword.

---

## Test Runner

```bash
# Run all tests
python run_tests.py --all

# Run specific category
python run_tests.py --category combinational
python run_tests.py --category sequential

# Run specific test
python run_tests.py --test combinational/operators/add_sub

# Run Level 2 (VCD comparison) only
python run_tests.py --level 2

# Run expect-fail tests only
python run_tests.py --category unsupported

# Run against a specific RyuSim version
python run_tests.py --all --ryusim-version 1.0.0

# Generate summary report
python run_tests.py --all --output results/latest.json
```

### Output Format

```json
{
  "ryusim_version": "1.0.0",
  "timestamp": "2026-02-02T12:00:00Z",
  "summary": {
    "total": 280,
    "passed": 268,
    "failed": 2,
    "expected_fail": 10,
    "skipped": 0
  },
  "categories": {
    "combinational": {"total": 120, "passed": 120},
    "sequential": {"total": 60, "passed": 58, "failed": 2},
    "hierarchy": {"total": 40, "passed": 40},
    "advanced": {"total": 30, "passed": 30},
    "unsupported": {"total": 30, "expected_fail": 30}
  },
  "failures": [
    {
      "test": "sequential/fsm/mealy_fsm",
      "stage": "execute",
      "error": "VCD mismatch at time 50ns: signal state expected 2'b10, got 2'b01"
    }
  ]
}
```

---

## CI Workflow

### test.yml

```yaml
name: SV Construct Tests

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
    inputs:
      ryusim_version:
        description: 'RyuSim version to test'
        required: false
        default: 'latest'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install RyuSim
        run: |
          RYUSIM_VERSION=${{ inputs.ryusim_version || 'latest' }} \
            curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install Verilator (for golden VCD generation)
        run: sudo apt-get install -y verilator

      - name: Run all tests
        run: python run_tests.py --all --output results/latest.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: results/
```

---

## Work Plan

| Step | Task |
|------|------|
| 1 | Create `ryusim-sv-tests` repo with directory structure |
| 2 | Write combinational/operators tests (20 tests) |
| 3 | Write combinational/arrays + structs + unions tests (31 tests) |
| 4 | Write remaining combinational tests (functions, generate, params, interfaces) |
| 5 | Write sequential/basic tests (flops, counters, shift registers) |
| 6 | Write sequential/fsm + memory tests |
| 7 | Write hierarchy + elaboration tests |
| 8 | Write advanced construct tests |
| 9 | Write expect-fail tests for unsupported constructs |
| 10 | Generate golden VCDs using Verilator |
| 11 | Create run_tests.py runner and test_manifest.json |
| 12 | Set up CI workflows |
| 13 | Run full suite against latest RyuSim release, report results |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Combinational tests passing | 120/120 |
| Sequential tests passing | 60/60 |
| Hierarchy tests passing | 40/40 |
| Advanced tests passing | 30/30 |
| Unsupported tests correctly rejected | 30/30 |
| Level 2 VCD matches | All sequential tests |

---

## Test Writing Guidelines

1. **One construct per test.** Each test should exercise a single SV construct or a closely related group.

2. **Minimal design.** Keep `.sv` files under 50 lines. No unnecessary signals or hierarchy.

3. **Self-checking cocotb tests.** Every test should have at least one assertion. Don't just check compilation — verify behavior.

4. **Deterministic.** No randomization in tests. All inputs and expected outputs are fixed.

5. **Naming convention:**
   - Directory: `category/subcategory/test_name/`
   - SV file: `dut.sv`
   - Test file: `test_<name>.py`
   - Makefile: standard cocotb Makefile

6. **Document the construct.** Add a brief comment at the top of `dut.sv` stating which IEEE 1800-2023 section is being tested.

```systemverilog
// IEEE 1800-2023 Section 11.4.12 - Conditional operator
module ternary_nested (...);
```

---

## Dependencies

### Required on test runner machine

| Tool | Purpose |
|------|---------|
| `ryusim` | Released binary (installed from ryusim.seiraiyu.com) |
| Python 3.10+ | Test runner and cocotb |
| cocotb | Python testbench framework |
| Verilator | Golden VCD generation |
| vcddiff | VCD comparison |

### RyuSim features relied upon

| Feature | Why Needed |
|---------|-----------|
| `ryusim compile` | Full pipeline: parse (Slang) + IR + codegen + build |
| VPI interface | Cocotb testbench integration |
| `--trace-vcd` | Waveform generation for Level 2 comparison |
| Error messages | Unsupported construct tests check error output |

---

## References

- [IEEE 1800-2023 SystemVerilog](https://standards.ieee.org/standard/1800-2023.html)
- [Slang language support](https://sv-lang.com/)
- [Benchmark tests plan](./2025-12-15-port-benchmark-tests-design.md)
- [RyuSim releases](https://ryusim.seiraiyu.com/releases/)
- [RyuSim GitHub](https://github.com/Seiraiyu/RyuSimAlt)
