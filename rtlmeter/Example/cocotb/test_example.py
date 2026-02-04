"""Cocotb testbench for the RTLMeter Example design.

The Example design is a synthesizable counter that counts from 0 to 1,000,000,
asserting a milestone flag every 200,000 cycles and a done flag at 1,000,000.
These tests validate that RyuSim can compile and simulate the design correctly.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


async def reset_dut(dut):
    """Apply active-low reset for 5 clock cycles."""
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_reset(dut):
    """Counter should be zero after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    await reset_dut(dut)

    assert int(dut.cnt.value) == 0, \
        f"Counter should be 0 after reset, got {int(dut.cnt.value)}"
    assert int(dut.done.value) == 0, \
        "Done flag should be de-asserted after reset"
    assert int(dut.milestone.value) == 0, \
        "Milestone flag should be de-asserted after reset"


@cocotb.test()
async def test_counter_increments(dut):
    """Counter should increment on each rising clock edge after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    await reset_dut(dut)

    # Run for 10 cycles and verify counter increments
    for expected in range(1, 11):
        await RisingEdge(dut.clk)
        actual = int(dut.cnt.value)
        assert actual == expected, \
            f"Expected cnt={expected}, got {actual}"


@cocotb.test()
async def test_smoke_100_cycles(dut):
    """Smoke test: run for 100 cycles without hanging, counter should reach 100."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    await reset_dut(dut)

    await ClockCycles(dut.clk, 100)

    actual = int(dut.cnt.value)
    assert actual == 100, \
        f"After 100 cycles counter should be 100, got {actual}"
    assert int(dut.done.value) == 0, \
        "Done flag should not be asserted after only 100 cycles"
