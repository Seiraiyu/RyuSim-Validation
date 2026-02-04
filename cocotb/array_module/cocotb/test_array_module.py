"""Cocotb testbench for array_module.

Validates that RyuSim can compile and simulate the array_module design
which includes various array types, structs, ascending/descending ranges,
parameters, and generate blocks.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_offset_passthrough(dut):
    """port_ofst_out should directly pass through port_ofst_in."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.select_in.value = 0
    dut.port_desc_in.value = 0
    dut.port_asc_in.value = 0
    dut.port_ofst_in.value = 0

    await ClockCycles(dut.clk, 2)

    test_val = 0xA5
    dut.port_ofst_in.value = test_val
    await ClockCycles(dut.clk, 2)

    assert int(dut.port_ofst_out.value) == test_val, \
        f"Expected offset passthrough {test_val:#x}, got {int(dut.port_ofst_out.value):#x}"


@cocotb.test()
async def test_select_param_values(dut):
    """With select_in == 0, outputs should reflect parameter default values."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.port_desc_in.value = 0
    dut.port_asc_in.value = 0
    dut.port_ofst_in.value = 0

    # select_in = 0 -> else branch -> param values
    dut.select_in.value = 0
    await ClockCycles(dut.clk, 3)

    # param_logic = 1'b1
    assert int(dut.port_logic_out.value) == 1, \
        f"Expected port_logic_out == 1 (param_logic), got {int(dut.port_logic_out.value)}"

    # param_logic_vec = 8'hDA
    assert int(dut.port_logic_vec_out.value) == 0xDA, \
        f"Expected port_logic_vec_out == 0xDA, got {int(dut.port_logic_vec_out.value):#x}"


@cocotb.test()
async def test_select_const_values(dut):
    """With select_in == 1, outputs should reflect localparam const values."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.port_desc_in.value = 0
    dut.port_asc_in.value = 0
    dut.port_ofst_in.value = 0

    # select_in = 1 -> const values
    dut.select_in.value = 1
    await ClockCycles(dut.clk, 3)

    # const_logic = 1'b0
    assert int(dut.port_logic_out.value) == 0, \
        f"Expected port_logic_out == 0 (const_logic), got {int(dut.port_logic_out.value)}"

    # const_logic_vec = 8'h3D
    assert int(dut.port_logic_vec_out.value) == 0x3D, \
        f"Expected port_logic_vec_out == 0x3D, got {int(dut.port_logic_vec_out.value):#x}"


@cocotb.test()
async def test_desc_data_path(dut):
    """Data driven on port_desc_in should appear on port_desc_out after a clock edge."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.select_in.value = 0
    dut.port_desc_in.value = 0
    dut.port_asc_in.value = 0
    dut.port_ofst_in.value = 0

    await ClockCycles(dut.clk, 2)

    test_val = 0xF0
    dut.port_desc_in.value = test_val
    await ClockCycles(dut.clk, 3)

    assert int(dut.port_desc_out.value) == test_val, \
        f"Expected desc output {test_val:#x}, got {int(dut.port_desc_out.value):#x}"
