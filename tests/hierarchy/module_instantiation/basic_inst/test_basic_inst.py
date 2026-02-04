import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_basic_instantiation(dut):
    """Test basic module instantiation: in_val=5 -> out_val=6."""
    dut.in_val.value = 5
    await Timer(1, units="ns")
    assert dut.out_val.value == 6


@cocotb.test()
async def test_overflow(dut):
    """Test 8-bit overflow: in_val=255 -> out_val=0."""
    dut.in_val.value = 255
    await Timer(1, units="ns")
    assert dut.out_val.value == 0
