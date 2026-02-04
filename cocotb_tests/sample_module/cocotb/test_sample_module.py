"""Cocotb testbench for sample_module.

Validates that RyuSim can compile and simulate the feature-rich sample_module
design which includes structs, generates, arrays, and mixed combinational/
sequential logic.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_stream_data_registered(dut):
    """Registered output should follow input data after one clock cycle."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.stream_in_valid.value = 0
    dut.stream_out_ready.value = 0
    dut.stream_in_data.value = 0
    dut.stream_in_data_dword.value = 0
    dut.stream_in_data_39bit.value = 0
    dut.stream_in_data_wide.value = 0
    dut.stream_in_data_dqword.value = 0
    dut.my_struct.value = 0

    await ClockCycles(dut.clk, 2)

    # Drive a known value and check it appears on registered output after a clock edge
    test_val = 0xAB
    dut.stream_in_data.value = test_val
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    assert int(dut.stream_out_data_registered.value) == test_val, \
        f"Expected registered output {test_val:#x}, got {int(dut.stream_out_data_registered.value):#x}"


@cocotb.test()
async def test_stream_data_combinational(dut):
    """Combinational output should reflect input data immediately."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.stream_in_valid.value = 0
    dut.stream_out_ready.value = 0
    dut.stream_in_data.value = 0
    dut.stream_in_data_dword.value = 0
    dut.stream_in_data_39bit.value = 0
    dut.stream_in_data_wide.value = 0
    dut.stream_in_data_dqword.value = 0
    dut.my_struct.value = 0

    await ClockCycles(dut.clk, 2)

    # Drive a value and verify combinational passthrough
    test_val = 0x5C
    dut.stream_in_data.value = test_val
    await ClockCycles(dut.clk, 1)

    assert int(dut.stream_out_data_comb.value) == test_val, \
        f"Expected combinational output {test_val:#x}, got {int(dut.stream_out_data_comb.value):#x}"


@cocotb.test()
async def test_and_gate(dut):
    """AND gate output should be stream_in_ready AND stream_in_valid."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.stream_in_data.value = 0
    dut.stream_in_data_dword.value = 0
    dut.stream_in_data_39bit.value = 0
    dut.stream_in_data_wide.value = 0
    dut.stream_in_data_dqword.value = 0
    dut.my_struct.value = 0

    # Both high -> AND output high
    dut.stream_out_ready.value = 1
    dut.stream_in_valid.value = 1
    await ClockCycles(dut.clk, 2)
    assert int(dut.and_output.value) == 1, "AND gate should be 1 when both inputs are 1"

    # One low -> AND output low
    dut.stream_in_valid.value = 0
    await ClockCycles(dut.clk, 2)
    assert int(dut.and_output.value) == 0, "AND gate should be 0 when one input is 0"


@cocotb.test()
async def test_ready_passthrough(dut):
    """stream_in_ready should follow stream_out_ready."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.stream_in_valid.value = 0
    dut.stream_in_data.value = 0
    dut.stream_in_data_dword.value = 0
    dut.stream_in_data_39bit.value = 0
    dut.stream_in_data_wide.value = 0
    dut.stream_in_data_dqword.value = 0
    dut.my_struct.value = 0

    dut.stream_out_ready.value = 1
    await ClockCycles(dut.clk, 2)
    assert int(dut.stream_in_ready.value) == 1, "stream_in_ready should follow stream_out_ready high"

    dut.stream_out_ready.value = 0
    await ClockCycles(dut.clk, 2)
    assert int(dut.stream_in_ready.value) == 0, "stream_in_ready should follow stream_out_ready low"
