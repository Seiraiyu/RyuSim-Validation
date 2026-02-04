"""Cocotb testbench for multi_dimension_array (cocotb_array).

Validates that RyuSim can compile and simulate a purely combinational
design with multi-dimensional packed/unpacked arrays, struct types,
and a package. The design is a passthrough — inputs are wired to outputs.
"""

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_packed_vector_passthrough(dut):
    """Packed vector input should pass through to output."""
    dut.in_vect_packed.value = 0b101
    await Timer(10, units="ns")

    assert int(dut.out_vect_packed.value) == 0b101, \
        f"Expected out_vect_packed == 0b101, got {int(dut.out_vect_packed.value):#05b}"


@cocotb.test()
async def test_2d_packed_packed_passthrough(dut):
    """2D packed-packed vector should pass through."""
    test_val = 0b101_010_111  # 9-bit value for [2:0][2:0]
    dut.in_2d_vect_packed_packed.value = test_val
    await Timer(10, units="ns")

    assert int(dut.out_2d_vect_packed_packed.value) == test_val, \
        f"Expected 2d packed-packed == {test_val:#011b}, got {int(dut.out_2d_vect_packed_packed.value):#011b}"


@cocotb.test()
async def test_3d_packed_passthrough(dut):
    """3D packed vector should pass through."""
    test_val = 0b101_010_111_000_110_001_011_100_010  # 27-bit for [2:0][2:0][2:0]
    dut.in_vect_packed_packed_packed.value = test_val
    await Timer(10, units="ns")

    assert int(dut.out_vect_packed_packed_packed.value) == test_val, \
        f"Expected 3d packed == {test_val:#029b}, got {int(dut.out_vect_packed_packed_packed.value):#029b}"


@cocotb.test()
async def test_struct_packed_passthrough(dut):
    """Packed struct input should pass through to output."""
    # struct_packed_t has: vect_packed[2:0], vect_packed_packed[2:0][2:0],
    # array_packed[2:0], array_packed_packed[2:0][2:0] = 3+9+3+9 = 24 bits
    test_val = 0xABCDEF & 0xFFFFFF  # 24 bits
    dut.in_struct_packed.value = test_val
    await Timer(10, units="ns")

    assert int(dut.out_struct_packed.value) == test_val, \
        f"Expected struct packed == {test_val:#08x}, got {int(dut.out_struct_packed.value):#08x}"


@cocotb.test()
async def test_arr_passthrough(dut):
    """test_array_entry_t (3-bit) should pass through."""
    test_val = 0b110
    dut.in_arr.value = test_val
    await Timer(10, units="ns")

    assert int(dut.out_arr.value) == test_val, \
        f"Expected arr == {test_val:#05b}, got {int(dut.out_arr.value):#05b}"
