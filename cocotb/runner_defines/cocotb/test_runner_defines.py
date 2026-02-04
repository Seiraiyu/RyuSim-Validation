"""Cocotb testbench for runner_defines.

The upstream design was empty (0 bytes). This tests a minimal synthesizable
placeholder — a parameterized shift register pipeline of configurable
width and depth.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_reset(dut):
    """Output should be 0 after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.data_in.value = 0xFF
    dut.reset.value = 1
    await ClockCycles(dut.clk, 5)

    assert int(dut.data_out.value) == 0x00, \
        f"Expected data_out == 0x00 during reset, got {int(dut.data_out.value):#04x}"


@cocotb.test()
async def test_pipeline_latency(dut):
    """Data should appear at output after DEPTH clock cycles (default DEPTH=4)."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.reset.value = 1
    dut.data_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 2)

    # Drive a known value
    test_val = 0xAB
    dut.data_in.value = test_val
    dut.data_in.value = test_val

    # Wait DEPTH cycles for data to propagate through the pipeline
    # Default DEPTH=4, so we need 4 clock cycles
    await ClockCycles(dut.clk, 5)

    assert int(dut.data_out.value) == test_val, \
        f"Expected data_out == {test_val:#04x} after pipeline latency, got {int(dut.data_out.value):#04x}"


@cocotb.test()
async def test_pipeline_clears_on_reset(dut):
    """Asserting reset mid-operation should clear the pipeline."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset and release
    dut.reset.value = 1
    dut.data_in.value = 0
    await ClockCycles(dut.clk, 3)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 2)

    # Fill pipeline with non-zero data
    dut.data_in.value = 0xFF
    await ClockCycles(dut.clk, 6)

    # Now assert reset
    dut.reset.value = 1
    await ClockCycles(dut.clk, 3)

    assert int(dut.data_out.value) == 0x00, \
        f"Expected data_out == 0x00 after mid-operation reset, got {int(dut.data_out.value):#04x}"
