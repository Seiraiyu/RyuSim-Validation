"""Cocotb testbench for runner.

Validates that RyuSim can compile and simulate a parameterized module
with configurable input and output widths. The runner module zero-extends
a narrow input to a wider output bus.
"""

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_zero_input(dut):
    """Zero input should produce zero output."""
    dut.data_in.value = 0
    await Timer(10, units="ns")

    assert int(dut.data_out.value) == 0, \
        f"Expected 0, got {int(dut.data_out.value)}"


@cocotb.test()
async def test_data_passthrough(dut):
    """Input value should appear in the lower bits of output."""
    test_val = 0xF  # max for 4-bit input (WIDTH_IN=4)
    dut.data_in.value = test_val
    await Timer(10, units="ns")

    assert int(dut.data_out.value) == test_val, \
        f"Expected {test_val:#04x}, got {int(dut.data_out.value):#04x}"


@cocotb.test()
async def test_zero_extension(dut):
    """Output upper bits should be zero (zero extension)."""
    dut.data_in.value = 0xF  # all 4 input bits set
    await Timer(10, units="ns")

    out_val = int(dut.data_out.value)
    # WIDTH_OUT=8, so output should be 0x0F (upper 4 bits zero)
    assert out_val == 0x0F, \
        f"Expected 0x0F (zero-extended), got {out_val:#04x}"


@cocotb.test()
async def test_multiple_values(dut):
    """Drive several values and verify zero-extension for each."""
    for val in range(16):  # all 4-bit values
        dut.data_in.value = val
        await Timer(10, units="ns")
        assert int(dut.data_out.value) == val, \
            f"For input {val}, expected output {val}, got {int(dut.data_out.value)}"
