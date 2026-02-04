# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

RyuSim-Validation is a consolidated test and benchmark suite that validates [RyuSim](https://github.com/Seiraiyu/RyuSimAlt), a hardware simulator that compiles synthesizable SystemVerilog to C++ and runs simulations via cocotb. The repo showcases RyuSim against real-world processor designs and exhaustive SystemVerilog construct tests.

RyuSim is consumed as an **installed binary**, never built from source:
```bash
curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash
```

## Architecture

The repo consolidates content ported from three upstream sources, preserving their basic structure:

| Directory | Source Repo | Purpose |
|-----------|------------|---------|
| `rtlmeter/` | [verilator/rtlmeter](https://github.com/verilator/rtlmeter) | Real-world processor benchmarks (VeeR, Vortex, XuanTie, BlackParrot) |
| `cocotb/` | [cocotb/cocotb/tests/designs](https://github.com/cocotb/cocotb/tree/master/tests/designs) | Reference test modules (uart2bus, array_module, sample_module, etc.) |
| `tests/` | [chipsalliance/UHDM-integration-tests](https://github.com/chipsalliance/UHDM-integration-tests) | SystemVerilog construct coverage (~280 tests across 5 categories) |

### Per-design/test structure

Every design follows this pattern:
```
design-name/
├── rtl/              # Synthesizable SystemVerilog (.sv/.v)
├── cocotb/           # Python testbenches (test_*.py)
├── Makefile          # cocotb invocation with SIM=ryusim
└── config.yaml       # Metadata
```

### Makefile pattern (cocotb)

```makefile
TOPLEVEL_LANG = verilog
SIM = ryusim
VERILOG_SOURCES = $(wildcard rtl/*.sv)
TOPLEVEL = module_name
MODULE = test_module_name
include $(shell cocotb-config --makefiles)/Makefile.sim
```

## Key RyuSim Constraints

- **No `$readmemh`**: Memory loading must be done via cocotb VPI array element access
- **No `initial begin`, `#` delays, `fork`/`join`**: RyuSim only supports synthesizable constructs
- **All simulation requires cocotb**: Clock generation, reset, stimulus, and termination are handled by cocotb testbenches
- **Compile command**: `ryusim compile design.sv --top module_name` (combines Slang parsing + IR + C++ codegen + build)
- **Output**: `obj_dir/build/module.so` (cocotb shared lib) + `obj_dir/build/module_sim` (standalone)
- **VCD tracing**: `ryusim compile design.sv --top module_name --trace-vcd`

### Memory loading via cocotb VPI (replaces $readmemh)

```python
async def load_hex(mem_array, hex_file):
    with open(hex_file) as f:
        for addr, line in enumerate(f):
            mem_array[addr].value = int(line.strip(), 16)
```

## Commands

```bash
# Install RyuSim
curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash

# Install cocotb (Seiraiyu fork with RyuSim backend support)
pip install git+https://github.com/Seiraiyu/cocotb.git

# Run a single design's tests via cocotb
cd rtlmeter/VeeR-EL2 && make      # uses SIM=ryusim from Makefile

# Run all benchmarks
python run_benchmarks.py --all
python run_benchmarks.py --design VeeR-EL2 --test dhrystone
python run_benchmarks.py --design VeeR-EL2 --compare-verilator

# Run SV construct tests
python run_tests.py --all
python run_tests.py --category combinational
python run_tests.py --test combinational/operators/add_sub
python run_tests.py --category unsupported   # expect-fail tests
python run_tests.py --level 2                # VCD comparison only
```

## Test Categories (SV construct tests)

| Category | Count | What it tests |
|----------|-------|---------------|
| `combinational/` | ~120 | `assign`, `always_comb`, operators, arrays, structs, enums, generate, interfaces |
| `sequential/` | ~60 | `always_ff`, `always_latch`, FSMs, memories, pipelines, clock domain |
| `hierarchy/` | ~40 | Module instantiation, parameters, packages, multi-file references |
| `advanced/` | ~30 | Typedefs, assertions (synthesis subset), `always @*`, multi-driven nets |
| `unsupported/` | ~30 | Expect-fail: `initial`, `fork`/`join`, classes, `$display` — validates error messages |

## Validation Levels

- **Level 1**: `ryusim compile` exits 0 and cocotb tests pass
- **Level 2**: VCD output matches Verilator golden references (via `vcddiff`)

## CI

GitHub Actions workflows with matrix builds across Linux distros. Each workflow installs RyuSim, cocotb, and optionally Verilator (for comparison), then runs the test suites.

## Dependencies

| Tool | Purpose |
|------|---------|
| `ryusim` | Installed binary — the simulator under test |
| Python 3.10+ | Test runners and cocotb |
| `cocotb` | [Seiraiyu fork](https://github.com/Seiraiyu/cocotb) with RyuSim backend — working toward an upstream PR to add RyuSim support |
| `Verilator` | Reference simulator for benchmarks and golden VCD generation |
| `vcddiff` | VCD waveform comparison (Level 2 validation) |
| RISC-V toolchain | Compile test programs (Dhrystone, CoreMark) for processor benchmarks |

## Design docs

Detailed design specifications live in `docs/`:
- `2025-12-15-port-benchmark-tests-design.md` — Benchmark test suite design (RTLMeter + cocotb designs)
- `2025-12-15-port-uhdm-integration-tests-design.md` — SV construct coverage test suite design
