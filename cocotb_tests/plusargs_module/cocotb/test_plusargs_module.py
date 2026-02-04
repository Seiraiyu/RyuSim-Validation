"""Cocotb testbench for plusargs_module (tb_top).

The upstream design was entirely non-synthesizable ($value$plusargs).
This tests a minimal synthesizable placeholder — a simple registered
data path with synchronous reset.
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
async def test_data_passthrough(dut):
    """After reset release, data_out should follow data_in on clock edges."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.reset.value = 1
    dut.data_in.value = 0
    await ClockCycles(dut.clk, 3)

    # Release reset
    dut.reset.value = 0
    await ClockCycles(dut.clk, 2)

    # Drive test value
    test_val = 0xA5
    dut.data_in.value = test_val
    await ClockCycles(dut.clk, 2)

    assert int(dut.data_out.value) == test_val, \
        f"Expected data_out == {test_val:#04x}, got {int(dut.data_out.value):#04x}"


@cocotb.test()
async def test_multiple_values(dut):
    """Drive several values and verify each appears on output."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.reset.value = 1
    dut.data_in.value = 0
    await ClockCycles(dut.clk, 3)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 2)

    for val in [0x00, 0xFF, 0x55, 0xAA, 0x01, 0x80]:
        dut.data_in.value = val
        await ClockCycles(dut.clk, 2)
        assert int(dut.data_out.value) == val, \
            f"Expected {val:#04x}, got {int(dut.data_out.value):#04x}"
