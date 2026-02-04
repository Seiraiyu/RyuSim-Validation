import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_split_aabb(dut):
    """Test struct field extraction: 0xAABB -> a=0xAA, b=0xBB."""
    dut.raw.value = 0xAABB
    await Timer(1, units="ns")
    assert dut.field_a.value == 0xAA
    assert dut.field_b.value == 0xBB


@cocotb.test()
async def test_split_1234(dut):
    """Test struct field extraction: 0x1234 -> a=0x12, b=0x34."""
    dut.raw.value = 0x1234
    await Timer(1, units="ns")
    assert dut.field_a.value == 0x12
    assert dut.field_b.value == 0x34
