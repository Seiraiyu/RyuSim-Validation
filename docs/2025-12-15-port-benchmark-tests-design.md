# RyuSim Benchmark Tests Design (RTLMeter + Cocotb)

**Date:** 2025-12-15 (original), 2026-02-02 (revised)
**Status:** Planned
**Repo:** `Seiraiyu/ryusim-benchmarks` (standalone)

## Overview

A standalone benchmark suite in its own repository that tests **released versions** of RyuSim against real-world processor designs. RyuSim is consumed as an installed binary, not built from source.

### Sources

1. **RTLMeter** (https://github.com/verilator/rtlmeter) - Real-world processor benchmarks
2. **Cocotb test designs** (https://github.com/cocotb/cocotb/tree/master/tests/designs) - Reference test modules

### Goals

- Port 18 designs (10 RTLMeter + 8 cocotb) for Tier 1
- Convert SystemVerilog testbenches to cocotb Python testbenches
- Create unified benchmark infrastructure
- Enable performance comparison against Verilator
- Track performance across RyuSim releases

### Key Decisions

**No $readmemh in RyuSim:**
- RyuSim requires cocotb for ALL simulation (clock, reset, stimulus, termination)
- Memory loading is done via cocotb VPI (array element access is implemented)
- Cocotb testbenches load hex files directly into memory arrays via VPI

```python
async def load_hex_to_memory(mem_array, hex_file):
    with open(hex_file, "r") as f:
        for addr, line in enumerate(f):
            mem_array[addr].value = int(line.strip(), 16)
```

---

## RyuSim Installation

The benchmark repo consumes released RyuSim binaries. No source build required.

```bash
# Install latest release
curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash

# Or pin a specific version
RYUSIM_VERSION=1.0.0 curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash

# Or download directly from GitHub releases
gh release download v1.0.0 --repo Seiraiyu/RyuSimAlt --pattern '*.tar.gz'
```

### RyuSim CLI Usage

```bash
# Compile a design (parse + IR + codegen + build in one step)
ryusim compile design.sv --top my_module

# Compile with VCD tracing
ryusim compile design.sv --top my_module --trace-vcd

# Output goes to obj_dir/ by default
# Produces: obj_dir/build/my_module.so (cocotb) + obj_dir/build/my_module_sim (standalone)
```

---

## Scope & Prioritization

### Tier 1: Immediate (18 designs)

#### RTLMeter Designs (10)

| Design | Initial Blocks | Description |
|--------|---------------|-------------|
| Example | 1 | Simple test design |
| Vortex | 3 | RISC-V GPU (Georgia Tech) |
| VeeR-EH1 | 3 | Western Digital RISC-V core |
| VeeR-EH2 | 6 | Western Digital RISC-V core |
| VeeR-EL2 | 8 | Western Digital RISC-V core |
| XuanTie-C906 | 2 | Alibaba T-Head RISC-V |
| XuanTie-C910 | 2 | Alibaba T-Head RISC-V |
| XuanTie-E902 | 2 | Alibaba T-Head RISC-V |
| XuanTie-E906 | 3 | Alibaba T-Head RISC-V |
| BlackParrot | 4 | Multi-core RISC-V (UW) |

#### Cocotb Designs (8)

| Design | Files | Notes |
|--------|-------|-------|
| uart2bus | 7 | Fully synthesizable UART-to-bus bridge |
| array_module | 1 | Array handling tests |
| basic_hierarchy_module | 1 | Hierarchy tests |
| multi_dimension_array | 2 | Multi-dim array tests |
| sample_module | 1 | Various SV constructs |
| plusargs_module | 1 | Plusargs handling |
| runner | 1 | Runner tests |
| runner_defines | 1 | Define handling |

*Skipped: vhdl_configurations, viterbi_decoder_axi4s (VHDL only)*

### Tier 2: Later (3 designs)

- OpenTitan (23 initial blocks) - Google secure microcontroller
- Caliptra (28 initial blocks) - Root-of-trust security core
- OpenPiton (48 initial blocks) - Princeton many-core processor

### Tier 3: Deferred (2 designs)

- NVDLA (640 initial blocks) - NVIDIA Deep Learning Accelerator
- XiangShan (2,898 initial blocks) - High-performance RISC-V

---

## Repository Structure

```
ryusim-benchmarks/
├── README.md
├── requirements.txt                # Python deps (cocotb, pytest, etc.)
├── setup_ryusim.sh                 # Download + install ryusim release
├── run_benchmarks.py               # Benchmark runner
├── benchmark_manifest.json         # All benchmarks metadata
│
├── .github/
│   └── workflows/
│       ├── benchmark.yml           # Run benchmarks on new RyuSim releases
│       └── nightly.yml             # Nightly regression against latest
│
├── rtlmeter/                       # RTLMeter designs
│   ├── Example/
│   │   ├── rtl/                    # Synthesizable RTL
│   │   ├── cocotb/                 # Python testbench
│   │   │   └── test_example.py
│   │   ├── Makefile                # cocotb Makefile
│   │   └── config.yaml             # Benchmark config
│   ├── VeeR-EL2/
│   │   ├── rtl/
│   │   ├── cocotb/
│   │   │   ├── test_hello.py
│   │   │   ├── test_dhrystone.py
│   │   │   └── test_coremark.py
│   │   ├── programs/               # Compiled test programs
│   │   │   ├── hello.hex
│   │   │   ├── dhrystone.hex
│   │   │   └── coremark.hex
│   │   ├── Makefile
│   │   └── config.yaml
│   └── .../                        # Other RTLMeter designs
│
├── cocotb/                         # Cocotb test designs
│   ├── uart2bus/
│   │   ├── rtl/
│   │   ├── cocotb/
│   │   │   └── test_uart2bus.py
│   │   ├── Makefile
│   │   └── config.yaml
│   └── .../                        # Other cocotb designs
│
└── results/                        # Benchmark results (gitignored)
    ├── v1.0.0.json
    └── latest.json
```

---

## Conversion Strategy

### Step 1: Extract Synthesizable RTL

For each design, separate:
- **Synthesizable RTL** -> `rtl/` directory
- **Testbench code** -> Discard (replaced with cocotb)

**Synthesizable criteria:**
- No `initial begin`
- No `$display`, `$finish`, `$fatal`
- No `fork`/`join`
- Uses `always_ff`, `always_comb`, `assign`

### Step 2: Convert Testbenches to Cocotb

**Original SV testbench:**
```systemverilog
initial begin
    $readmemh("program.hex", dut.imem);
    reset = 1;
    #100 reset = 0;

    wait(dut.done);
    $display("Cycles: %d", dut.cycle_count);
    $finish;
end
```

**Converted cocotb testbench:**
```python
async def load_hex(mem, filename):
    """Load hex file into memory via VPI"""
    with open(filename) as f:
        for addr, line in enumerate(f):
            mem[addr].value = int(line.strip(), 16)

@cocotb.test()
async def test_program(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Load program into memory via VPI
    await load_hex(dut.cpu.imem, "program.hex")

    # Reset sequence
    dut.reset.value = 1
    await ClockCycles(dut.clk, 10)
    dut.reset.value = 0

    # Wait for completion
    while dut.done.value != 1:
        await ClockCycles(dut.clk, 100)

    cycles = dut.cycle_count.value
    cocotb.log.info(f"Cycles: {cycles}")
```

### Step 3: Create Makefile per Design

Each design gets a cocotb Makefile that invokes ryusim:

```makefile
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = top_module
MODULE = cocotb.test_design

include $(shell cocotb-config --makefiles)/Makefile.sim
```

---

## Metrics & Benchmarking

### Metrics Collected (matching RTLMeter)

| Metric | Description | Stage |
|--------|-------------|-------|
| elapsed | Wall clock time (seconds) | All |
| user | CPU user time | All |
| system | CPU system time | All |
| memory | Peak memory (MB) | All |
| clocks | Simulated clock cycles | Execute |
| speed | Simulation speed (kHz) | Execute |
| codeSize | Generated C++ size (MB) | Compile |

### Stages Measured

```
1. compile  → ryusim compile (parse + IR + codegen + C++ build)
2. execute  → cocotb simulation run
```

Note: RyuSim's `compile` command combines parsing (via Slang), IR conversion, C++ code generation, and building into a single step. The benchmark runner can measure the overall compile time and the simulation execution time separately.

### Benchmark Runner

```bash
# Run all benchmarks
python run_benchmarks.py --all

# Run specific design
python run_benchmarks.py --design VeeR-EL2

# Run specific test
python run_benchmarks.py --design VeeR-EL2 --test dhrystone

# Compare against Verilator
python run_benchmarks.py --design VeeR-EL2 --compare-verilator

# Output JSON results
python run_benchmarks.py --all --output results.json

# Run against a specific RyuSim version
python run_benchmarks.py --all --ryusim-version 1.0.0
```

### Output Format

```json
{
  "ryusim_version": "1.0.0",
  "design": "VeeR-EL2",
  "test": "dhrystone",
  "iterations": 10000,
  "ryusim": {
    "compile": {"elapsed": 18.4, "memory": 1024, "codeSize": 2.3},
    "execute": {"elapsed": 5.4, "clocks": 50000, "speed": 9259, "memory": 512}
  },
  "verilator": {
    "verilate": {"elapsed": 8.1, "memory": 1200},
    "compile": {"elapsed": 22.3, "memory": 1500},
    "execute": {"elapsed": 4.2, "clocks": 50000, "speed": 11904, "memory": 800}
  }
}
```

---

## CI Workflow

The benchmark repo has its own CI that downloads released RyuSim binaries.

### benchmark.yml

Triggered on: push to main, or manually with a RyuSim version input.

```yaml
name: Benchmarks

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      ryusim_version:
        description: 'RyuSim version to benchmark'
        required: false
        default: 'latest'

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install RyuSim
        run: |
          RYUSIM_VERSION=${{ inputs.ryusim_version || 'latest' }} \
            curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install Verilator
        run: sudo apt-get install -y verilator

      - name: Run benchmarks
        run: python run_benchmarks.py --all --output results/latest.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: results/
```

### nightly.yml

Nightly regression against the latest RyuSim release to catch performance regressions.

---

## Work Plan

| Step | Task |
|------|------|
| 1 | Create `ryusim-benchmarks` repo with structure above |
| 2 | Port cocotb uart2bus (fully synthesizable, quick win) |
| 3 | Port cocotb simple designs (7 designs) |
| 4 | Port RTLMeter Example design |
| 5 | Port RTLMeter VeeR-EL2 + write cocotb tests |
| 6 | Port RTLMeter VeeR-EH1/EH2 |
| 7 | Port RTLMeter Vortex |
| 8 | Port RTLMeter XuanTie designs (4) |
| 9 | Port RTLMeter BlackParrot |
| 10 | Create benchmark_manifest.json |
| 11 | Create run_benchmarks.py runner |
| 12 | Set up CI workflows |
| 13 | Run all benchmarks and verify pass |
| 14 | Generate comparison report vs Verilator |

---

## Success Criteria

### Porting Success

| Metric | Target |
|--------|--------|
| Cocotb designs ported | 8/10 (skip 2 VHDL) |
| RTLMeter Tier 1 designs ported | 10/10 |
| Cocotb testbenches written | 1 per design minimum |
| All tests passing | 100% |

### Benchmark Validation

| Check | Criteria |
|-------|----------|
| Compile success | `ryusim compile` exits 0 for all designs |
| Execute success | All cocotb tests pass |
| Functional correctness | VCD comparison matches Verilator (for subset) |

### Performance Baseline

Initial benchmarks establish baseline - no specific performance targets.
Future iterations track regressions/improvements across releases.

---

## Dependencies

### Required on benchmark runner machine

| Tool | Purpose |
|------|---------|
| `ryusim` | Released binary (installed from ryusim.seiraiyu.com) |
| Python 3.10+ | Benchmark runner and cocotb |
| cocotb | Python testbench framework |
| Verilator | Reference for comparison benchmarks |
| vcddiff | VCD comparison |
| RISC-V toolchain | Compile test programs (Dhrystone, CoreMark) |

### RyuSim features relied upon

| Feature | Why Needed |
|---------|-----------|
| `ryusim compile` | Full pipeline: parse (Slang) + IR + codegen + build |
| VPI interface | Cocotb testbench integration |
| VPI array access | Memory loading via cocotb |
| `--trace-vcd` | Waveform generation for VCD comparison |

---

## What These Designs Are

### RTLMeter - Real RISC-V/GPU Processors

| Design | Description |
|--------|-------------|
| VeeR-EL2/EH1/EH2 | Western Digital's RISC-V CPU cores (production silicon) |
| Vortex | RISC-V GPU (Georgia Tech academic project) |
| XuanTie C906/C910/E902/E906 | Alibaba T-Head's RISC-V CPU cores |
| BlackParrot | Multi-core RISC-V processor (University of Washington) |
| OpenTitan | Google's open-source secure microcontroller |
| Caliptra | Root-of-trust security core (AMD, Google, Microsoft, NVIDIA) |
| NVDLA | NVIDIA Deep Learning Accelerator |
| OpenPiton | Princeton's many-core research processor |
| XiangShan | Chinese Academy of Sciences high-performance RISC-V |

### Cocotb - Test/Reference Modules

| Design | Description |
|--------|-------------|
| uart2bus | UART serial-to-bus bridge (real synthesizable IP) |
| sample_module | Test module with various SV constructs |
| array_module | Array handling tests |
| viterbi_decoder_axi4s | Viterbi decoder with AXI4-Stream (VHDL) |

---

## References

- [RTLMeter repo](https://github.com/verilator/rtlmeter)
- [Cocotb test designs](https://github.com/cocotb/cocotb/tree/master/tests/designs)
- [SV construct coverage plan](./2025-12-15-port-uhdm-integration-tests-design.md)
- [RyuSim releases](https://ryusim.seiraiyu.com/releases/)
- [RyuSim GitHub](https://github.com/Seiraiyu/RyuSimAlt)
