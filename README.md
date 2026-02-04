# RyuSim-Validation

A consolidated test and benchmark suite for validating [RyuSim](https://github.com/Seiraiyu/RyuSimAlt), a hardware simulator that compiles synthesizable SystemVerilog to C++ and runs simulations via [cocotb](https://github.com/Seiraiyu/cocotb).

## What's Inside

| Directory | Source | Contents |
|-----------|--------|----------|
| `rtlmeter_tests/` | [verilator/rtlmeter](https://github.com/verilator/rtlmeter) | 10 real-world processor benchmarks (VeeR-EL2, Vortex GPU, BlackParrot, XuanTie cores) |
| `cocotb_tests/` | [cocotb/cocotb](https://github.com/cocotb/cocotb/tree/master/tests/designs) | 8 reference cocotb test designs (uart2bus, array_module, sample_module, etc.) |
| `uhdm_tests/` | [chipsalliance/UHDM-integration-tests](https://github.com/chipsalliance/UHDM-integration-tests) | 27 SystemVerilog construct tests across 5 categories |

### Benchmark Designs (18 total)

**RTLMeter processors:**
VeeR-EL2, VeeR-EH1, VeeR-EH2, Vortex (RISC-V GPU), BlackParrot (multicore), XuanTie-C906, XuanTie-C910, XuanTie-E902, XuanTie-E906, Example

**Cocotb reference designs:**
uart2bus, sample_module, array_module, basic_hierarchy_module, multi_dimension_array, plusargs_module, runner, runner_defines

### SV Construct Tests (27 total)

| Category | Tests | What it covers |
|----------|-------|----------------|
| `combinational` | 15 | Operators, arrays, structs, enums, generate blocks |
| `sequential` | 5 | D flip-flops, FSMs, register files |
| `hierarchy` | 3 | Module instantiation, parameters, packages |
| `advanced` | 2 | Typedefs, assertions |
| `unsupported` | 2 | Expect-fail: `initial` blocks, `fork`/`join` |

## Quick Start

```bash
# Install RyuSim
curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash

# Install cocotb (Seiraiyu fork with RyuSim backend)
pip install git+https://github.com/Seiraiyu/cocotb.git

# Install Python dependencies
pip install -r requirements.txt

# Run all benchmarks
python run_benchmarks.py --all

# Run all SV construct tests
python run_tests.py --all

# Or use make
make install    # install all dependencies
make benchmarks # run benchmarks
make tests      # run SV tests
make all        # run everything
```

## Running Tests

### Benchmarks

```bash
python run_benchmarks.py --all                              # all 18 designs
python run_benchmarks.py --design VeeR-EL2                  # single design
python run_benchmarks.py --design VeeR-EL2 --compare-verilator  # with Verilator comparison
python run_benchmarks.py --all --output results/bench.json  # JSON output
python run_benchmarks.py --all -v                           # verbose progress
```

### SV Construct Tests

```bash
python run_tests.py --all                                       # all 27 tests
python run_tests.py --category combinational                    # by category
python run_tests.py --test combinational/operators/add_sub      # single test
python run_tests.py --all --level 2                             # VCD comparison mode
python run_tests.py --all --output results/sv-tests.json        # JSON output
```

### Individual Designs

Each design can be run directly via its Makefile:

```bash
cd rtlmeter_tests/VeeR-EL2 && make
cd cocotb_tests/uart2bus && make
cd uhdm_tests/combinational/operators/add_sub && make
```

## Validation Levels

- **Level 1**: `ryusim compile` succeeds and cocotb tests pass
- **Level 2**: VCD output matches Verilator golden references (via `vcddiff`)

Generate golden VCDs (requires Verilator):

```bash
python generate_golden_vcds.py --category sequential
python generate_golden_vcds.py --all
```

## Project Structure

```
RyuSim-Validation/
├── rtlmeter_tests/          # Processor benchmark designs (10)
│   ├── VeeR-EL2/            #   Each design has:
│   │   ├── rtl/             #     Synthesizable SystemVerilog
│   │   ├── cocotb/          #     Python testbenches
│   │   ├── Makefile         #     cocotb invocation (SIM=ryusim)
│   │   └── config.yaml      #     Design metadata
│   ├── Vortex/
│   ├── BlackParrot/
│   └── ...
├── cocotb_tests/            # Reference cocotb designs (8)
│   ├── uart2bus/
│   ├── sample_module/
│   └── ...
├── uhdm_tests/              # SV construct tests (27)
│   ├── combinational/       #   Operators, arrays, structs, enums, generate
│   ├── sequential/          #   Flip-flops, FSMs, memories
│   ├── hierarchy/           #   Instantiation, parameters, packages
│   ├── advanced/            #   Typedefs, assertions
│   └── unsupported/         #   Expect-fail tests
├── golden/                  # Verilator reference VCDs
├── results/                 # Test output (gitignored)
├── run_benchmarks.py        # Benchmark runner
├── run_tests.py             # SV test runner
├── generate_golden_vcds.py  # Golden VCD generation
├── Makefile                 # Convenience targets
├── requirements.txt         # Python dependencies
├── setup_ryusim.sh          # RyuSim installation helper
└── .github/workflows/       # CI pipelines
```

## CI

Three GitHub Actions workflows run on push/PR:

- **benchmarks.yml** -- Runs all benchmark designs on Ubuntu 22.04/24.04
- **sv-tests.yml** -- Runs SV construct tests on push to `uhdm_tests/`
- **nightly.yml** -- Full Level 2 validation suite at 6 AM UTC daily

## Key RyuSim Constraints

RyuSim compiles **synthesizable SystemVerilog only**. This means:

- No `initial begin`, `#` delays, `fork`/`join`
- No `$readmemh` -- memory loading done via cocotb VPI
- No `$display`, `$finish` -- simulation controlled by cocotb
- All clock generation, reset, and stimulus handled by cocotb testbenches

## Dependencies

| Tool | Purpose |
|------|---------|
| [RyuSim](https://github.com/Seiraiyu/RyuSimAlt) | Simulator under test |
| Python 3.10+ | Test runners and cocotb |
| [cocotb](https://github.com/Seiraiyu/cocotb) (Seiraiyu fork) | Python testbench framework with RyuSim backend |
| [Verilator](https://verilator.org) | Reference simulator for golden VCDs |
| vcddiff | VCD waveform comparison (Level 2) |

## License

Individual designs retain their upstream licenses. See `LICENSE` files in each design directory.
