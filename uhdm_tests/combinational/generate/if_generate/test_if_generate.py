import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_add_small(dut):
    """Test addition with default USE_ADD=1: 10 + 20 = 30."""
    dut.a.value = 10
    dut.b.value = 20
    await Timer(1, units="ns")
    assert dut.result.value == 30


@cocotb.test()
async def test_add_overflow(dut):
    """Test addition overflow with USE_ADD=1: 255 + 1 = 256."""
    dut.a.value = 255
    dut.b.value = 1
    await Timer(1, units="ns")
    assert dut.result.value == 256
