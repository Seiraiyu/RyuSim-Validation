"""Cocotb testbench for uart2bus_top.

Validates that RyuSim can compile and simulate the uart2bus design.
Tests focus on reset behavior and basic signal integrity rather than
full UART protocol compliance.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer


@cocotb.test()
async def test_reset(dut):
    """uart2bus_top should come out of reset with outputs in known idle state."""
    cocotb.start_soon(Clock(dut.clock, 10, units="ns").start())

    # Hold serial input high (UART idle line)
    dut.ser_in.value = 1
    # No bus grant during reset
    dut.int_gnt.value = 0
    # No read data
    dut.int_rd_data.value = 0

    # Assert reset
    dut.reset.value = 1
    await ClockCycles(dut.clock, 10)

    # Release reset
    dut.reset.value = 0
    await ClockCycles(dut.clock, 10)

    # After reset, verify idle state:
    # - ser_out should be high (UART idle)
    assert dut.ser_out.value == 1, "ser_out should be high (idle) after reset"
    # - No bus write or read activity
    assert dut.int_write.value == 0, "int_write should be low after reset"
    assert dut.int_read.value == 0, "int_read should be low after reset"
    # - No bus request
    assert dut.int_req.value == 0, "int_req should be low after reset"


@cocotb.test()
async def test_idle_no_activity(dut):
    """With ser_in held high (idle), no bus transactions should occur."""
    cocotb.start_soon(Clock(dut.clock, 10, units="ns").start())

    # Hold inputs in idle state
    dut.ser_in.value = 1
    dut.int_gnt.value = 0
    dut.int_rd_data.value = 0

    # Reset sequence
    dut.reset.value = 1
    await ClockCycles(dut.clock, 10)
    dut.reset.value = 0
    await ClockCycles(dut.clock, 5)

    # Run for many cycles with idle input
    for _ in range(50):
        await RisingEdge(dut.clock)
        assert dut.int_write.value == 0, "int_write should remain low during idle"
        assert dut.int_read.value == 0, "int_read should remain low during idle"
        assert dut.ser_out.value == 1, "ser_out should remain high during idle"
