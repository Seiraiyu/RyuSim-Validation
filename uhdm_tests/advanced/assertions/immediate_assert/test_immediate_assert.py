import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_sum_basic(dut):
    """Test basic addition: a=100, b=50 -> sum=150."""
    dut.a.value = 100
    dut.b.value = 50
    await Timer(1, units="ns")
    assert dut.sum.value == 150


@cocotb.test()
async def test_sum_overflow(dut):
    """Test 9-bit sum: a=255, b=255 -> sum=510."""
    dut.a.value = 255
    dut.b.value = 255
    await Timer(1, units="ns")
    assert dut.sum.value == 510
