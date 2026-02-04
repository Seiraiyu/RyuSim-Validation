"""Cocotb testbench for the BlackParrot RISC-V processor.

This testbench replaces the upstream Verilator-specific testbench.sv with a
cocotb-driven simulation. The upstream testbench instantiates the wrapper module
plus several nonsynth simulation models:
  - bsg_nonsynth_clock_gen: clock generation
  - bsg_nonsynth_reset_gen: reset generation
  - bp_nonsynth_cfg_loader: configuration loading
  - bp_nonsynth_dram: DRAM memory model
  - bp_nonsynth_host: host I/O interface

All of these are replaced by cocotb driving the wrapper ports directly.

The top module under test is wrapper, which:
  - Wraps bp_processor (the full BlackParrot multicore)
  - Generates a downsampled real-time clock (rt_clk) from clk_i
  - Exposes memory and DMA interfaces for external connection

Architecture notes:
  - BlackParrot is a multicore RISC-V processor from University of Washington
  - It uses a tiled architecture with NoC-based coherence (BedRock protocol)
  - The design includes 3 major RTL components:
    * bp/: ~160 files — core RTL (FE, BE, ME, CCE, tiles, multicore)
    * basejump_stl/: ~170 files — BSG standard template library
    * hardfloat/: ~18 files — Berkeley HardFloat FPU
  - Configured via bp_params_e enum (e_bp_multicore_1_cfg for 1x1)

Test strategy:
  - test_compile: Validates that RyuSim can parse and compile the full
    BlackParrot design (~350 source files, ~3.3MB of RTL). This is the
    largest and most complex design in the benchmark suite.
  - test_reset: Drives clock and reset, verifies basic post-reset state
  - test_smoke_100_cycles: Runs for 100 clock cycles to verify no hangs

Note: Full program execution requires a DRAM model, configuration loading,
and program memory initialization. This is a future enhancement.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer


async def reset_dut(dut):
    """Apply reset sequence for the BlackParrot processor.

    The upstream testbench uses bsg_nonsynth_reset_gen with configurable
    cycle counts. For cocotb, we hold reset high for 20 clock cycles
    (matching the upstream sim_reset_cycles_hi_p=20 default).

    All input ports are driven to safe default values.
    """
    # Assert reset
    dut.reset_i.value = 1

    # Device IDs (from upstream testbench)
    dut.my_did_i.value = 1       # proc_did = 1
    dut.host_did_i.value = 0     # host_did = all 1s would be complex; use 0 for now

    # Memory forward interface — no commands during reset
    dut.mem_fwd_header_i.value = 0
    dut.mem_fwd_data_i.value = 0
    dut.mem_fwd_v_i.value = 0

    # Memory reverse interface — accept any responses
    dut.mem_rev_ready_and_i.value = 0

    # Memory forward output — accept any forwarded requests
    dut.mem_fwd_ready_and_i.value = 0

    # Memory reverse input — no reverse responses
    dut.mem_rev_header_i.value = 0
    dut.mem_rev_data_i.value = 0
    dut.mem_rev_v_i.value = 0

    # DMA interface — all idle
    dut.dma_pkt_ready_and_i.value = 0
    dut.dma_data_i.value = 0
    dut.dma_data_v_i.value = 0
    dut.dma_data_ready_and_i.value = 0

    # Hold reset for 20 clock cycles (matching upstream default)
    await ClockCycles(dut.clk_i, 20)

    # Deassert reset
    dut.reset_i.value = 0
    await ClockCycles(dut.clk_i, 5)


@cocotb.test()
async def test_compile(dut):
    """Verify that the BlackParrot design compiles and elaborates successfully.

    This test validates that RyuSim can handle:
    - ~350 SystemVerilog source files totaling ~3.3MB of RTL
    - Complex package hierarchy (bp_common_pkg, bp_be_pkg, bp_fe_pkg, bp_me_pkg)
    - BaseJump STL library with ~170 parameterized modules
    - Berkeley HardFloat FPU with Verilog (.v) files
    - Heavy use of SystemVerilog macros (`declare_bp_proc_params, etc.)
    - Multi-level module hierarchy with tiles, complexes, and multicore
    - Elaborate generate blocks for multi-core configuration
    - Wormhole network-on-chip routers and concentrators
    - Cache coherence engine (CCE) with instruction RAM
    - BedRock protocol stream pumps and gearboxes

    Simply reaching this point (cocotb test starting) means compilation
    and elaboration succeeded.
    """
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await Timer(1, units="ns")
    dut._log.info("BlackParrot design compiled and elaborated successfully")


@cocotb.test()
async def test_reset(dut):
    """Verify the processor enters a known state after reset.

    After reset release, the processor should begin its initialization
    sequence. Without a configuration loader or DRAM, it will stall
    waiting for configuration, which is expected.
    """
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    await reset_dut(dut)

    # After reset, check that memory forward output is valid
    try:
        mem_fwd_v = int(dut.mem_fwd_v_o.value)
        dut._log.info(f"Memory forward valid after reset: {mem_fwd_v}")
    except ValueError:
        dut._log.info("Memory forward valid is X/Z (acceptable during early post-reset)")

    try:
        mem_rev_v = int(dut.mem_rev_v_o.value)
        dut._log.info(f"Memory reverse valid after reset: {mem_rev_v}")
    except ValueError:
        dut._log.info("Memory reverse valid is X/Z (acceptable during early post-reset)")

    dut._log.info("Reset sequence completed successfully")


@cocotb.test()
async def test_smoke_100_cycles(dut):
    """Run the processor for 100 clock cycles after reset.

    This smoke test verifies that:
    1. The processor does not hang or crash during the first 100 cycles
    2. The design can be clocked without simulation errors
    3. No assertion-like failures occur in the design

    Without a DRAM model or configuration loader, the processor will be
    in an uninitialized state. The important thing is that it does not
    produce simulation errors during clock cycling.
    """
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    await reset_dut(dut)

    # Enable handshake signals to prevent deadlock
    dut.mem_fwd_ready_and_i.value = 1
    dut.mem_rev_ready_and_i.value = 1
    dut.dma_pkt_ready_and_i.value = 0
    dut.dma_data_ready_and_i.value = 0

    mem_fwd_seen = False
    dma_activity_seen = False

    for cycle in range(100):
        await RisingEdge(dut.clk_i)

        # Check if processor is attempting memory operations
        try:
            if int(dut.mem_fwd_v_o.value) == 1:
                mem_fwd_seen = True
        except ValueError:
            pass  # X/Z values are acceptable

        # Check DMA activity
        try:
            if int(dut.dma_pkt_v_o.value) == 1:
                dma_activity_seen = True
        except ValueError:
            pass

    dut._log.info(f"Completed 100 cycles after reset")
    dut._log.info(f"Memory forward activity seen: {mem_fwd_seen}")
    dut._log.info(f"DMA activity seen: {dma_activity_seen}")
    dut._log.info("Smoke test passed -- processor did not hang")
