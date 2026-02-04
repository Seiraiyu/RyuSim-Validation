import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_nested_aabbcc(dut):
    """Test nested struct: 0xAABBCC -> x=0xAA, y=0xBB, z=0xCC."""
    dut.raw.value = 0xAABBCC
    await Timer(1, units="ns")
    assert dut.inner_x.value == 0xAA
    assert dut.inner_y.value == 0xBB
    assert dut.outer_z.value == 0xCC


@cocotb.test()
async def test_nested_112233(dut):
    """Test nested struct: 0x112233 -> x=0x11, y=0x22, z=0x33."""
    dut.raw.value = 0x112233
    await Timer(1, units="ns")
    assert dut.inner_x.value == 0x11
    assert dut.inner_y.value == 0x22
    assert dut.outer_z.value == 0x33
