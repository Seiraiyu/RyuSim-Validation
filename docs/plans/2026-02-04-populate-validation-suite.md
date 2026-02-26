# RyuSim Validation Suite — Full Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Populate the RyuSim-Validation scaffold with real content: 8 cocotb design ports, 10 rtlmeter benchmark ports, ~30 initial SV construct tests, working runner scripts, and golden VCD infrastructure.

**Architecture:** Three independent workstreams feeding into shared runner infrastructure. Cocotb designs are ported first (smallest, prove the workflow), then SV construct tests (self-contained, high value), then rtlmeter benchmarks (largest, require upstream RTL extraction). Runner scripts are implemented alongside the first workstream so every subsequent task can be validated end-to-end.

**Tech Stack:** Python 3.11, cocotb (Seiraiyu fork), RyuSim (installed binary), Verilator (golden reference), PyYAML, Make

---

## Prerequisites

Before starting, ensure:
- RyuSim is installed: `ryusim --version` works
- Cocotb Seiraiyu fork is installed: `pip install git+https://github.com/Seiraiyu/cocotb.git`
- Verilator is installed: `verilator --version` works
- Python deps: `pip install -r requirements.txt`

The upstream repos should be cloned into `.upstream/` for RTL extraction:
```bash
git clone https://github.com/verilator/rtlmeter.git .upstream/rtlmeter
git clone https://github.com/cocotb/cocotb.git .upstream/cocotb
```

---

## Phase 1: Runner Infrastructure + First Cocotb Design (Tasks 1-5)

Build the runner scripts with real execution logic, validated against one working design.

### Task 1: Implement run_tests.py execution logic

**Files:**
- Modify: `run_tests.py`
- Modify: `run_benchmarks.py`

**Step 1: Implement `run_test()` in `run_tests.py`**

Replace the stub `run_test()` function with real logic that:
1. Reads `config.yaml` from the test directory
2. Checks if the test is in the `unsupported` category
3. For supported tests: runs `make` in the test directory (which invokes cocotb with SIM=ryusim), captures exit code and output
4. For unsupported tests: runs `ryusim compile dut.sv --top <module>`, asserts exit code != 0, checks stderr against `expected_error.txt`
5. For level 2: additionally runs `vcddiff` comparing output VCD against golden

The function signature stays the same: `run_test(test_path, level=1)` -> dict.

Key implementation details:
- Use `subprocess.run()` with `capture_output=True`, `text=True`, `cwd=test_path`, `timeout=300`
- Parse `config.yaml` with `yaml.safe_load()` to get `top_module` and other metadata
- Return dict with keys: `test`, `path`, `category`, `level`, `status` (passed/failed/expected_fail/error), `duration`, `stdout`, `stderr`
- Add a `ryusim_version` field to the summary output (run `ryusim --version` once at start)
- Add a `timestamp` field with ISO 8601 datetime

**Step 2: Implement `run_benchmark()` in `run_benchmarks.py`**

Replace the stub `run_benchmark()` function with real logic that:
1. Reads `config.yaml` from the design directory
2. Runs `make` in the design directory (cocotb with SIM=ryusim)
3. Captures timing via `time.perf_counter()` around the subprocess call
4. Optionally runs Verilator comparison if `compare_verilator=True`
5. Collects metrics: elapsed time, exit code, stdout/stderr

Return dict matching the JSON output format from the design doc:
```python
{
    "design": design_path.name,
    "path": str(design_path),
    "test": test_name,
    "ryusim": {
        "compile": {"elapsed": ..., "status": ...},
        "execute": {"elapsed": ..., "status": ...},
    },
    "status": "passed" / "failed" / "error",
    "duration": ...,
}
```

**Step 3: Add `--verbose` flag to both scripts**

Add a `--verbose` / `-v` flag that prints per-test progress to stderr as tests run (test name, status, duration).

**Step 4: Run and verify**

```bash
python run_tests.py --help
python run_benchmarks.py --help
# Both should exit 0 with updated help text showing --verbose
```

**Step 5: Commit**

```bash
git add run_tests.py run_benchmarks.py
git commit -m "feat: implement runner execution logic in run_tests.py and run_benchmarks.py"
```

---

### Task 2: Clone upstream repos and port uart2bus RTL

**Files:**
- Create: `.upstream/` clones (gitignored)
- Create: `cocotb/uart2bus/rtl/*.v` (copied from upstream)
- Modify: `cocotb/uart2bus/config.yaml`
- Modify: `cocotb/uart2bus/Makefile`

**Step 1: Clone upstream cocotb repo**

```bash
mkdir -p .upstream
git clone --depth 1 https://github.com/cocotb/cocotb.git .upstream/cocotb
```

**Step 2: Copy uart2bus RTL into the design directory**

The upstream path is `.upstream/cocotb/tests/designs/uart2bus/`.
- Copy all `.v` and `.sv` files from `uart2bus/` (NOT from any `hdl/` or `rtl/` subdirectory — check upstream structure first) into `cocotb/uart2bus/rtl/`
- Inspect each file: remove any `initial begin` blocks, `$readmemh`, `$display`, `$finish`, `#` delays, `timescale` directives
- If a file is entirely non-synthesizable (pure testbench), skip it

**Step 3: Identify the top module**

Read the RTL files to find the top-level module name. Update `config.yaml`:
```yaml
name: uart2bus
source: cocotb
tier: 1
description: "UART serial-to-bus bridge"
top_module: "uart2bus_top"
```

**Step 4: Update Makefile**

```makefile
# uart2bus — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = uart2bus_top
MODULE = test_uart2bus

include $(shell cocotb-config --makefiles)/Makefile.sim
```

Replace `uart2bus_top` with the actual top module name found in step 3.

**Step 5: Verify compilation**

```bash
cd cocotb/uart2bus
ryusim compile rtl/*.v --top <top_module>
# Should exit 0
```

**Step 6: Commit**

```bash
git add cocotb/uart2bus/
git commit -m "feat: port uart2bus RTL from upstream cocotb"
```

---

### Task 3: Write uart2bus cocotb testbench

**Files:**
- Create: `cocotb/uart2bus/cocotb/test_uart2bus.py`

**Step 1: Study the upstream testbench**

Read `.upstream/cocotb/tests/designs/uart2bus/` for any existing testbenches. Understand:
- What signals the top module exposes (clk, reset, uart_rx, uart_tx, bus addr/data/wr/rd)
- What the expected behavior is

**Step 2: Write a cocotb testbench**

Create `cocotb/uart2bus/cocotb/test_uart2bus.py`:
- Import cocotb, Clock, Timer, RisingEdge
- Create a clock on `dut.clk`
- Apply reset (drive `dut.rst` high for 10 cycles, then low)
- Write a basic smoke test: assert the design doesn't hang after reset
- If the design has bus read/write signals, write a test that writes a value and reads it back

Every test must use `@cocotb.test()` decorator and `async def`.

**Step 3: Update Makefile MODULE path**

Ensure the `MODULE` in the Makefile points to the correct Python module name. Since the test file is `test_uart2bus.py`, set `MODULE = test_uart2bus`.

**Step 4: Run the test**

```bash
cd cocotb/uart2bus
make
# Should compile with ryusim and run cocotb tests
```

**Step 5: Commit**

```bash
git add cocotb/uart2bus/
git commit -m "feat: add cocotb testbench for uart2bus"
```

---

### Task 4: Port remaining 7 cocotb designs

**Files:**
- Modify: `cocotb/sample_module/` (rtl/, config.yaml, Makefile, cocotb/)
- Modify: `cocotb/array_module/` (same)
- Modify: `cocotb/basic_hierarchy_module/` (same)
- Modify: `cocotb/multi_dimension_array/` (same)
- Modify: `cocotb/plusargs_module/` (same)
- Modify: `cocotb/runner/` (same)
- Modify: `cocotb/runner_defines/` (same)

For each of the 7 remaining designs, repeat the same process as Tasks 2-3:

**Step 1: Copy RTL from upstream**

For each design, find the upstream source in `.upstream/cocotb/tests/designs/<name>/`:
- Copy all `.v`/`.sv` files into the design's `rtl/` directory
- Strip non-synthesizable constructs (initial blocks, delays, system tasks)
- Some designs may be single-file (e.g., `sample_module` is one `.sv` file)

**Step 2: Identify top module and update config.yaml + Makefile**

Read the RTL to find the top module. Update both files with the correct module name and a description.

**Step 3: Write cocotb testbench**

For each design, create `cocotb/test_<name>.py` with:
- Clock generation (if the design has a clock input)
- Reset sequence (if the design has a reset input)
- At least one `@cocotb.test()` that exercises the design's primary function and includes an assertion

Keep tests simple — the goal is proving RyuSim can compile and simulate the design, not exhaustive verification.

**Step 4: Verify each design compiles and tests pass**

```bash
cd cocotb/<design_name> && make
```

Run for each design. Fix any compilation or test issues.

**Step 5: Commit after each design (or batch if small)**

```bash
git add cocotb/<design_name>/
git commit -m "feat: port <design_name> from upstream cocotb"
```

Commit per design or in batches of 2-3 related designs.

---

### Task 5: Validate cocotb runner end-to-end

**Files:**
- None new (validation only)

**Step 1: Run benchmarks runner against all cocotb designs**

```bash
python run_benchmarks.py --all
```

Should discover all 8 cocotb designs and report results.

**Step 2: Run with JSON output**

```bash
python run_benchmarks.py --all --output results/cocotb-test.json
cat results/cocotb-test.json
```

Verify the JSON structure matches the design doc format.

**Step 3: Run single design**

```bash
python run_benchmarks.py --design uart2bus
```

**Step 4: Fix any issues found, commit**

```bash
git add -u
git commit -m "fix: resolve runner issues found during cocotb validation"
```

---

## Phase 2: SV Construct Tests (Tasks 6-12)

Build out the SystemVerilog construct test suite, starting with combinational (highest count, simplest).

### Task 6: Create first combinational test — operators/add_sub

**Files:**
- Create: `tests/combinational/operators/add_sub/dut.sv`
- Create: `tests/combinational/operators/add_sub/test_add_sub.py`
- Create: `tests/combinational/operators/add_sub/Makefile`
- Create: `tests/combinational/operators/add_sub/config.yaml`
- Remove: `tests/combinational/operators/.gitkeep`

**Step 1: Write dut.sv**

```systemverilog
// IEEE 1800-2023 Section 11.4.3 - Arithmetic operators
module add_sub (
    input  logic [7:0] a, b,
    input  logic       op,  // 0=add, 1=sub
    output logic [8:0] result
);
    assign result = op ? (a - b) : (a + b);
endmodule
```

**Step 2: Write test_add_sub.py**

```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_add(dut):
    """Test addition: 10 + 20 = 30."""
    dut.a.value = 10
    dut.b.value = 20
    dut.op.value = 0
    await Timer(1, units="ns")
    assert dut.result.value == 30

@cocotb.test()
async def test_sub(dut):
    """Test subtraction: 30 - 10 = 20."""
    dut.a.value = 30
    dut.b.value = 10
    dut.op.value = 1
    await Timer(1, units="ns")
    assert dut.result.value == 20

@cocotb.test()
async def test_overflow(dut):
    """Test addition overflow: 255 + 1 = 256 (9 bits)."""
    dut.a.value = 255
    dut.b.value = 1
    dut.op.value = 0
    await Timer(1, units="ns")
    assert dut.result.value == 256
```

**Step 3: Write Makefile**

```makefile
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = dut.sv
TOPLEVEL = add_sub
MODULE = test_add_sub

include $(shell cocotb-config --makefiles)/Makefile.sim
```

**Step 4: Write config.yaml**

```yaml
name: add_sub
category: combinational
subcategory: operators
description: "Arithmetic addition and subtraction operators"
top_module: add_sub
ieee_section: "11.4.3"
level: 1
```

**Step 5: Compile and run**

```bash
cd tests/combinational/operators/add_sub
make
# Should pass all 3 tests
```

**Step 6: Verify test runner discovers it**

```bash
python run_tests.py --test combinational/operators/add_sub
```

**Step 7: Commit**

```bash
git add tests/combinational/operators/add_sub/
git rm tests/combinational/operators/.gitkeep
git commit -m "feat: add combinational/operators/add_sub SV construct test"
```

---

### Task 7: Create combinational operator tests batch

**Files:**
- Create: `tests/combinational/operators/bitwise/` (dut.sv, test, Makefile, config.yaml)
- Create: `tests/combinational/operators/logical/` (same)
- Create: `tests/combinational/operators/shift/` (same)
- Create: `tests/combinational/operators/reduction/` (same)
- Create: `tests/combinational/operators/comparison/` (same)
- Create: `tests/combinational/operators/ternary/` (same)

For each test, follow the same pattern as Task 6:

**bitwise** — Tests AND, OR, XOR, NOT, NAND, NOR, XNOR:
```systemverilog
module bitwise (
    input  logic [7:0] a, b,
    output logic [7:0] and_out, or_out, xor_out, not_out
);
    assign and_out = a & b;
    assign or_out  = a | b;
    assign xor_out = a ^ b;
    assign not_out = ~a;
endmodule
```

**logical** — Tests &&, ||, !:
```systemverilog
module logical (
    input  logic [7:0] a, b,
    output logic       and_out, or_out, not_out
);
    assign and_out = a && b;
    assign or_out  = a || b;
    assign not_out = !a;
endmodule
```

**shift** — Tests <<, >>, <<<, >>>:
```systemverilog
module shift (
    input  logic signed [7:0] a,
    input  logic [2:0] amt,
    output logic [7:0] lsl_out, lsr_out,
    output logic signed [7:0] asr_out
);
    assign lsl_out = a << amt;
    assign lsr_out = a >> amt;
    assign asr_out = a >>> amt;
endmodule
```

**reduction** — Tests &, |, ^, ~& (and reduction), ~| (or reduction), ~^ (xnor reduction):
```systemverilog
module reduction (
    input  logic [7:0] a,
    output logic       and_r, or_r, xor_r
);
    assign and_r = &a;
    assign or_r  = |a;
    assign xor_r = ^a;
endmodule
```

**comparison** — Tests ==, !=, <, >, <=, >=, ===, !==:
```systemverilog
module comparison (
    input  logic [7:0] a, b,
    output logic       eq, neq, lt, gt, lte, gte
);
    assign eq  = (a == b);
    assign neq = (a != b);
    assign lt  = (a < b);
    assign gt  = (a > b);
    assign lte = (a <= b);
    assign gte = (a >= b);
endmodule
```

**ternary** — Tests conditional operator, nested:
```systemverilog
module ternary (
    input  logic [7:0] a, b, c,
    input  logic [1:0] sel,
    output logic [7:0] out
);
    assign out = (sel == 2'b00) ? a :
                 (sel == 2'b01) ? b : c;
endmodule
```

Each test gets a cocotb testbench with 2-4 test cases exercising key behaviors.

**Commit after completing all operator tests:**

```bash
git add tests/combinational/operators/
git commit -m "feat: add combinational operator tests (bitwise, logical, shift, reduction, comparison, ternary)"
```

---

### Task 8: Create combinational array, struct, enum tests

**Files:**
- Create: `tests/combinational/arrays/packed_array/` (dut.sv, test, Makefile, config.yaml)
- Create: `tests/combinational/arrays/unpacked_array/` (same)
- Create: `tests/combinational/structs/packed_struct/` (same)
- Create: `tests/combinational/structs/nested_struct/` (same)
- Create: `tests/combinational/enums/basic_enum/` (same)
- Create: `tests/combinational/enums/enum_methods/` (same)

**packed_array dut.sv:**
```systemverilog
module packed_array (
    input  logic [3:0][7:0] data_in,
    input  logic [1:0]      sel,
    output logic [7:0]      data_out
);
    assign data_out = data_in[sel];
endmodule
```

**packed_struct dut.sv:**
```systemverilog
module packed_struct (
    input  logic [15:0] raw,
    output logic [7:0]  field_a,
    output logic [7:0]  field_b
);
    typedef struct packed {
        logic [7:0] a;
        logic [7:0] b;
    } my_struct_t;

    my_struct_t s;
    assign s = raw;
    assign field_a = s.a;
    assign field_b = s.b;
endmodule
```

**basic_enum dut.sv:**
```systemverilog
module basic_enum (
    input  logic [1:0] sel,
    output logic [7:0] out
);
    typedef enum logic [1:0] {
        IDLE  = 2'b00,
        RUN   = 2'b01,
        DONE  = 2'b10,
        ERROR = 2'b11
    } state_t;

    state_t state;
    assign state = state_t'(sel);
    assign out = (state == IDLE)  ? 8'd0 :
                 (state == RUN)   ? 8'd1 :
                 (state == DONE)  ? 8'd2 : 8'd255;
endmodule
```

Follow the same pattern: dut.sv + test_*.py + Makefile + config.yaml for each. Cocotb tests should exercise boundary conditions.

Remove `.gitkeep` files from populated directories.

**Commit:**

```bash
git add tests/combinational/arrays/ tests/combinational/structs/ tests/combinational/enums/
git commit -m "feat: add combinational tests for arrays, structs, and enums"
```

---

### Task 9: Create combinational generate tests

**Files:**
- Create: `tests/combinational/generate/for_generate/` (dut.sv, test, Makefile, config.yaml)
- Create: `tests/combinational/generate/if_generate/` (same)

**for_generate dut.sv:**
```systemverilog
module for_generate #(
    parameter WIDTH = 8
)(
    input  logic [WIDTH-1:0] a, b,
    output logic [WIDTH-1:0] result
);
    genvar i;
    generate
        for (i = 0; i < WIDTH; i++) begin : gen_xor
            assign result[i] = a[i] ^ b[i];
        end
    endgenerate
endmodule
```

**if_generate dut.sv:**
```systemverilog
module if_generate #(
    parameter USE_ADD = 1
)(
    input  logic [7:0] a, b,
    output logic [8:0] result
);
    generate
        if (USE_ADD) begin : gen_add
            assign result = a + b;
        end else begin : gen_sub
            assign result = a - b;
        end
    endgenerate
endmodule
```

**Commit:**

```bash
git add tests/combinational/generate/
git commit -m "feat: add combinational generate tests (for_generate, if_generate)"
```

---

### Task 10: Create sequential tests

**Files:**
- Create: `tests/sequential/basic_flops/d_ff/` (dut.sv, test, Makefile, config.yaml)
- Create: `tests/sequential/basic_flops/d_ff_async_rst/` (same)
- Create: `tests/sequential/basic_flops/enabled_ff/` (same)
- Create: `tests/sequential/fsm/moore_fsm/` (same)
- Create: `tests/sequential/memories/register_file/` (same)

**d_ff dut.sv:**
```systemverilog
module d_ff (
    input  logic clk,
    input  logic rst,
    input  logic d,
    output logic q
);
    always_ff @(posedge clk) begin
        if (rst)
            q <= 1'b0;
        else
            q <= d;
    end
endmodule
```

**d_ff test_d_ff.py:**
```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_reset(dut):
    """D-FF should output 0 after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.d.value = 1
    await ClockCycles(dut.clk, 3)
    assert dut.q.value == 0

@cocotb.test()
async def test_capture(dut):
    """D-FF should capture input on rising clock edge."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    dut.d.value = 1
    await ClockCycles(dut.clk, 2)
    assert dut.q.value == 1
```

**moore_fsm dut.sv:**
```systemverilog
module moore_fsm (
    input  logic clk,
    input  logic rst,
    input  logic in_bit,
    output logic [1:0] state_out
);
    typedef enum logic [1:0] {
        S0 = 2'b00,
        S1 = 2'b01,
        S2 = 2'b10
    } state_t;

    state_t state, next_state;

    always_ff @(posedge clk) begin
        if (rst)
            state <= S0;
        else
            state <= next_state;
    end

    always_comb begin
        case (state)
            S0: next_state = in_bit ? S1 : S0;
            S1: next_state = in_bit ? S2 : S0;
            S2: next_state = S0;
            default: next_state = S0;
        endcase
    end

    assign state_out = state;
endmodule
```

**register_file dut.sv:**
```systemverilog
module register_file #(
    parameter DEPTH = 8,
    parameter WIDTH = 8
)(
    input  logic                    clk,
    input  logic                    wr_en,
    input  logic [$clog2(DEPTH)-1:0] wr_addr, rd_addr,
    input  logic [WIDTH-1:0]        wr_data,
    output logic [WIDTH-1:0]        rd_data
);
    logic [WIDTH-1:0] mem [DEPTH];

    always_ff @(posedge clk) begin
        if (wr_en)
            mem[wr_addr] <= wr_data;
    end

    assign rd_data = mem[rd_addr];
endmodule
```

Sequential tests require cocotb `Clock` and `ClockCycles`. Each test must create a clock and apply reset before testing.

Remove `.gitkeep` from populated subdirectories.

**Commit:**

```bash
git add tests/sequential/
git commit -m "feat: add sequential tests (d_ff, d_ff_async_rst, enabled_ff, moore_fsm, register_file)"
```

---

### Task 11: Create hierarchy and advanced tests

**Files:**
- Create: `tests/hierarchy/module_instantiation/basic_inst/` (dut.sv, test, Makefile, config.yaml)
- Create: `tests/hierarchy/parameters/param_override/` (same)
- Create: `tests/hierarchy/packages/basic_package/` (same)
- Create: `tests/advanced/typedefs/basic_typedef/` (same)
- Create: `tests/advanced/assertions/immediate_assert/` (same)

**basic_inst dut.sv** (multi-file: inner.sv + top.sv):
```systemverilog
// inner.sv
module inner (
    input  logic [7:0] a,
    output logic [7:0] b
);
    assign b = a + 8'd1;
endmodule
```
```systemverilog
// top.sv
module basic_inst (
    input  logic [7:0] in_val,
    output logic [7:0] out_val
);
    inner u_inner (
        .a(in_val),
        .b(out_val)
    );
endmodule
```

Makefile for multi-file: `VERILOG_SOURCES = inner.sv top.sv` (list explicitly or use wildcard).

**param_override dut.sv:**
```systemverilog
module param_override #(
    parameter WIDTH = 8,
    parameter INIT  = 0
)(
    input  logic [WIDTH-1:0] a,
    output logic [WIDTH-1:0] b
);
    assign b = a + INIT[WIDTH-1:0];
endmodule
```

Cocotb test should verify behavior with default parameters (the Makefile just compiles with defaults).

**basic_package dut.sv:**
```systemverilog
package my_pkg;
    typedef logic [7:0] byte_t;
    localparam byte_t MAGIC = 8'hAB;
endpackage

module basic_package (
    input  my_pkg::byte_t data_in,
    output my_pkg::byte_t data_out,
    output logic          is_magic
);
    assign data_out = data_in;
    assign is_magic = (data_in == my_pkg::MAGIC);
endmodule
```

**basic_typedef dut.sv:**
```systemverilog
module basic_typedef (
    input  logic [15:0] raw,
    output logic [7:0]  high, low
);
    typedef logic [7:0] byte_t;
    byte_t h, l;
    assign {h, l} = raw;
    assign high = h;
    assign low = l;
endmodule
```

Remove `.gitkeep` from populated subdirectories.

**Commit:**

```bash
git add tests/hierarchy/ tests/advanced/
git commit -m "feat: add hierarchy and advanced SV construct tests"
```

---

### Task 12: Create unsupported construct (expect-fail) tests

**Files:**
- Create: `tests/unsupported/initial_block/dut.sv`
- Create: `tests/unsupported/initial_block/expected_error.txt`
- Create: `tests/unsupported/initial_block/config.yaml`
- Create: `tests/unsupported/fork_join/dut.sv`
- Create: `tests/unsupported/fork_join/expected_error.txt`
- Create: `tests/unsupported/fork_join/config.yaml`

**initial_block/dut.sv:**
```systemverilog
module bad_initial (
    output logic [7:0] o
);
    initial begin
        o = 8'hFF;
    end
endmodule
```

**initial_block/expected_error.txt:**
```
initial
```

**initial_block/config.yaml:**
```yaml
name: initial_block
category: unsupported
subcategory: initial_block
description: "Verify ryusim rejects initial blocks"
top_module: bad_initial
expect_fail: true
```

**fork_join/dut.sv:**
```systemverilog
module bad_fork (
    input logic clk,
    output logic [7:0] o
);
    initial begin
        fork
            o = 8'h01;
        join
    end
endmodule
```

**fork_join/expected_error.txt:**
```
fork
```

**fork_join/config.yaml:**
```yaml
name: fork_join
category: unsupported
subcategory: fork_join
description: "Verify ryusim rejects fork/join"
top_module: bad_fork
expect_fail: true
```

Note: These tests do NOT have Makefiles or cocotb test files — the runner invokes `ryusim compile` directly and checks for failure.

The `run_test()` function (Task 1) handles expect-fail tests by:
1. Running `ryusim compile dut.sv --top <module>` in the test directory
2. Asserting exit code != 0
3. Checking that stderr contains the keyword from `expected_error.txt`
4. Returning status `expected_fail` on success

Remove `.gitkeep` from populated subdirectories.

**Commit:**

```bash
git add tests/unsupported/
git commit -m "feat: add unsupported construct expect-fail tests (initial_block, fork_join)"
```

---

### Task 13: Validate SV test runner end-to-end

**Files:**
- None new (validation only)

**Step 1: Run all SV tests**

```bash
python run_tests.py --all
```

Should discover all tests across all categories and report results.

**Step 2: Run by category**

```bash
python run_tests.py --category combinational
python run_tests.py --category sequential
python run_tests.py --category unsupported
```

**Step 3: Run single test**

```bash
python run_tests.py --test combinational/operators/add_sub
```

**Step 4: Run with JSON output**

```bash
python run_tests.py --all --output results/sv-tests-initial.json
cat results/sv-tests-initial.json
```

Verify JSON structure matches design doc.

**Step 5: Fix any issues, commit**

```bash
git add -u
git commit -m "fix: resolve SV test runner issues found during validation"
```

---

## Phase 3: RTLMeter Benchmark Ports (Tasks 14-19)

Port real-world processor designs from upstream rtlmeter. Start with the Example design, then VeeR-EL2 (most important), then batch the rest.

### Task 14: Clone upstream rtlmeter and port Example design

**Files:**
- Create: `.upstream/rtlmeter/` (gitignored)
- Create: `rtlmeter/Example/rtl/*.sv`
- Modify: `rtlmeter/Example/config.yaml`
- Modify: `rtlmeter/Example/Makefile`
- Create: `rtlmeter/Example/cocotb/test_example.py`

**Step 1: Clone upstream rtlmeter**

```bash
git clone --depth 1 https://github.com/verilator/rtlmeter.git .upstream/rtlmeter
```

**Step 2: Examine the Example design**

Look at `.upstream/rtlmeter/designs/example/` (or similar — find the actual path). Identify:
- All RTL source files
- Top module name
- Any `initial begin` blocks, `$readmemh`, or other non-synthesizable code

**Step 3: Copy and clean RTL**

- Copy synthesizable `.sv`/`.v` files to `rtlmeter/Example/rtl/`
- Remove any `initial begin`, `$readmemh`, `$display`, `$finish`, `#` delays
- If the design loads memory via `$readmemh`, note the memory path for cocotb VPI loading

**Step 4: Update config.yaml and Makefile**

```yaml
name: Example
source: rtlmeter
tier: 1
description: "RTLMeter example test design"
top_module: <actual_top_module>
```

**Step 5: Write cocotb testbench**

Create `rtlmeter/Example/cocotb/test_example.py`:
- Clock + reset sequence
- Basic smoke test (run for N cycles, check no hang)

**Step 6: Compile and test**

```bash
cd rtlmeter/Example && make
```

**Step 7: Commit**

```bash
git add rtlmeter/Example/
git commit -m "feat: port Example design from upstream rtlmeter"
```

---

### Task 15: Port VeeR-EL2 design

**Files:**
- Create: `rtlmeter/VeeR-EL2/rtl/*.sv` (many files)
- Modify: `rtlmeter/VeeR-EL2/config.yaml`
- Modify: `rtlmeter/VeeR-EL2/Makefile`
- Create: `rtlmeter/VeeR-EL2/cocotb/test_hello.py`
- Create: `rtlmeter/VeeR-EL2/programs/hello.hex`

This is the flagship benchmark. VeeR-EL2 is a production RISC-V core from Western Digital.

**Step 1: Examine upstream VeeR-EL2 in rtlmeter**

Look at `.upstream/rtlmeter/designs/VeeR-EL2/` to understand:
- RTL file list and include paths
- Top module name (likely `el2_swerv_wrapper` or similar)
- Number of `initial begin` blocks (documented as 8)
- How memory is loaded (likely `$readmemh` on IRAM/DRAM)

**Step 2: Copy synthesizable RTL**

This will be many files. Copy the entire RTL directory, then:
- Remove all `initial begin` blocks
- Remove `$readmemh` calls (note which memories they load)
- Remove `$display`, `$finish`
- Keep all `always_ff`, `always_comb`, `assign`, module instantiations

**Step 3: Create hello program hex file**

The upstream rtlmeter likely includes test program hex files or Makefiles to build them. If available, copy `hello.hex` into `programs/`.

If not available, a minimal hex file can be created that writes a known value to a memory-mapped register.

**Step 4: Write cocotb testbench**

Create `rtlmeter/VeeR-EL2/cocotb/test_hello.py`:
```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

async def load_hex(mem, filename):
    """Load hex file into memory via VPI."""
    with open(filename) as f:
        for addr, line in enumerate(f):
            word = line.strip()
            if word:
                mem[addr].value = int(word, 16)

@cocotb.test()
async def test_hello(dut):
    """Load hello program and run until completion."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Load program into instruction memory via VPI
    await load_hex(dut.<path_to_imem>, "programs/hello.hex")

    # Reset
    dut.rst_l.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_l.value = 1

    # Run for up to 10000 cycles
    for _ in range(10000):
        await ClockCycles(dut.clk, 100)
        # Check for completion signal (design-specific)
```

The exact memory path (`dut.<path_to_imem>`) and reset signal names depend on the VeeR-EL2 design. These must be determined by reading the RTL.

**Step 5: Update config.yaml**

```yaml
name: VeeR-EL2
source: rtlmeter
tier: 1
description: "Western Digital VeeR EL2 RISC-V core"
top_module: <actual_top>
programs:
  - hello.hex
```

**Step 6: Compile and test**

```bash
cd rtlmeter/VeeR-EL2 && make
```

This will likely require debugging — VeeR-EL2 is a complex design.

**Step 7: Commit**

```bash
git add rtlmeter/VeeR-EL2/
git commit -m "feat: port VeeR-EL2 design from upstream rtlmeter"
```

---

### Task 16: Port VeeR-EH1 and VeeR-EH2

**Files:**
- Modify: `rtlmeter/VeeR-EH1/` (rtl/, config.yaml, Makefile, cocotb/)
- Modify: `rtlmeter/VeeR-EH2/` (same)

Same process as VeeR-EL2 (Task 15). These are related cores from the same family, so the porting process should be similar:
- Same memory loading pattern (VPI instead of `$readmemh`)
- Same general testbench structure
- Different top module names and signal paths

**Commit each design separately.**

---

### Task 17: Port Vortex and BlackParrot

**Files:**
- Modify: `rtlmeter/Vortex/` (rtl/, config.yaml, Makefile, cocotb/)
- Modify: `rtlmeter/BlackParrot/` (same)

**Vortex** is a RISC-V GPU from Georgia Tech. It has 3 initial blocks to remove.

**BlackParrot** is a multi-core RISC-V processor from University of Washington. It has 4 initial blocks.

Both designs are more complex than VeeR. The cocotb testbenches should:
1. Create clock
2. Apply reset
3. Run for a fixed number of cycles
4. Verify no hang (timeout-based test)

Full functional verification comes later — the goal here is compilation + basic simulation.

**Commit each design separately.**

---

### Task 18: Port XuanTie designs (C906, C910, E902, E906)

**Files:**
- Modify: `rtlmeter/XuanTie-C906/` (rtl/, config.yaml, Makefile, cocotb/)
- Modify: `rtlmeter/XuanTie-C910/` (same)
- Modify: `rtlmeter/XuanTie-E902/` (same)
- Modify: `rtlmeter/XuanTie-E906/` (same)

All four XuanTie cores are from Alibaba T-Head. They have 2-3 initial blocks each.

The porting process is the same: extract synthesizable RTL, remove `initial begin`/`$readmemh`, write basic cocotb testbenches.

These can be batch-committed in pairs:
```bash
git commit -m "feat: port XuanTie-C906 and XuanTie-C910 from upstream rtlmeter"
git commit -m "feat: port XuanTie-E902 and XuanTie-E906 from upstream rtlmeter"
```

---

### Task 19: Validate rtlmeter runner end-to-end

**Files:**
- None new (validation only)

**Step 1: Run all benchmarks**

```bash
python run_benchmarks.py --all
```

Should discover all 18 designs (10 rtlmeter + 8 cocotb).

**Step 2: Run with JSON output**

```bash
python run_benchmarks.py --all --output results/benchmarks-initial.json
```

**Step 3: Run single design**

```bash
python run_benchmarks.py --design VeeR-EL2
```

**Step 4: Fix issues, commit**

```bash
git add -u
git commit -m "fix: resolve benchmark runner issues found during rtlmeter validation"
```

---

## Phase 4: Golden VCD Infrastructure (Tasks 20-21)

### Task 20: Generate golden VCDs for sequential tests

**Files:**
- Create: `golden/sequential/basic_flops/d_ff.vcd`
- Create: `golden/sequential/basic_flops/d_ff_async_rst.vcd`
- Create: `golden/sequential/basic_flops/enabled_ff.vcd`
- Create: `golden/sequential/fsm/moore_fsm.vcd`
- Create: `golden/sequential/memories/register_file.vcd`

**Step 1: Run each sequential test with Verilator to generate golden VCDs**

For each test in `tests/sequential/`:
```bash
cd tests/sequential/basic_flops/d_ff
SIM=verilator make
cp sim_build/dump.vcd ../../../../golden/sequential/basic_flops/d_ff.vcd
make clean
```

Repeat for all sequential tests.

**Step 2: Run level 2 validation**

```bash
python run_tests.py --category sequential --level 2
```

The runner should compare RyuSim's VCD output against the golden VCDs using `vcddiff`.

**Step 3: Commit golden VCDs**

```bash
git add golden/
git commit -m "feat: add golden VCDs for sequential tests (Verilator reference)"
```

---

### Task 21: Final validation and cleanup

**Files:**
- None new

**Step 1: Run complete validation suite**

```bash
python run_tests.py --all --level 1 --output results/final-l1.json
python run_tests.py --category sequential --level 2 --output results/final-l2.json
python run_benchmarks.py --all --output results/final-benchmarks.json
```

**Step 2: Run `make check`**

```bash
make check
```

**Step 3: Verify CI workflows would work**

```bash
python -c "import yaml; [yaml.safe_load(open(f)) for f in ['.github/workflows/benchmarks.yml', '.github/workflows/sv-tests.yml', '.github/workflows/nightly.yml']]"
```

**Step 4: Clean up any remaining .gitkeep files in populated directories**

```bash
find . -name .gitkeep -not -path './golden/*' -not -path './results/*' | while read f; do
    dir=$(dirname "$f")
    count=$(find "$dir" -not -name .gitkeep -not -name "$(basename $dir)" -type f | wc -l)
    if [ "$count" -gt 0 ]; then
        echo "Remove: $f (directory has $count other files)"
        git rm "$f"
    fi
done
```

**Step 5: Final commit**

```bash
git add -u
git commit -m "chore: final cleanup — remove redundant .gitkeep files, validation passing"
```

---

## Summary

| Phase | Tasks | What it delivers |
|-------|-------|-----------------|
| 1 | 1-5 | Working runners + 8 cocotb design ports |
| 2 | 6-13 | ~30 SV construct tests across all 5 categories |
| 3 | 14-19 | 10 rtlmeter processor benchmark ports |
| 4 | 20-21 | Golden VCD infrastructure + final validation |

Total: 21 tasks, each independently committable.
