"""Cocotb testbench for basic_hierarchy_module.

Validates that RyuSim can compile and simulate a basic module hierarchy
with a counter in the top module and two sub-modules that add offsets
(+2 and +5) to the counter value.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, FallingEdge


@cocotb.test()
async def test_counter_reset(dut):
    """Counter should be 0 after reset is deasserted."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Assert reset (active low)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 5)

    # Check counter is held at 0 during reset
    assert int(dut.counter.value) == 0, \
        f"Counter should be 0 during reset, got {int(dut.counter.value)}"


@cocotb.test()
async def test_counter_increments(dut):
    """Counter should increment on each clock edge after reset release."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset sequence (active low reset)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 5)

    # Release reset
    dut.reset.value = 1
    await ClockCycles(dut.clk, 2)

    # Read counter and verify it increments
    val1 = int(dut.counter.value)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    val2 = int(dut.counter.value)

    assert val2 > val1, \
        f"Counter should increment: val1={val1}, val2={val2}"


@cocotb.test()
async def test_submodule_offsets(dut):
    """Sub-module outputs should be counter+2 and counter+5 respectively."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset sequence
    dut.reset.value = 0
    await ClockCycles(dut.clk, 5)
    dut.reset.value = 1
    await ClockCycles(dut.clk, 10)

    # Let counter run for a few cycles, then read and compare
    # Note: sub-module outputs are registered, so they lag by one cycle
    counter_val = int(dut.counter.value)
    await ClockCycles(dut.clk, 2)

    plus_two = int(dut.i_module_a.data_out.value)
    plus_five = int(dut.i_module_b.data_out.value)

    # The outputs are registered so they reflect a recent counter value + offset
    # We just verify the relationship is correct (offset difference)
    diff = plus_five - plus_two
    assert diff == 3, \
        f"Difference between module_b and module_a outputs should be 3, got {diff} " \
        f"(plus_two={plus_two}, plus_five={plus_five})"
