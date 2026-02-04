import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_split_aabb(dut):
    """Test typedef byte split: raw=0xAABB -> high=0xAA, low=0xBB."""
    dut.raw.value = 0xAABB
    await Timer(1, units="ns")
    assert dut.high.value == 0xAA
    assert dut.low.value == 0xBB


@cocotb.test()
async def test_split_1234(dut):
    """Test typedef byte split: raw=0x1234 -> high=0x12, low=0x34."""
    dut.raw.value = 0x1234
    await Timer(1, units="ns")
    assert dut.high.value == 0x12
    assert dut.low.value == 0x34
