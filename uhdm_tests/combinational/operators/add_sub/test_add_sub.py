import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_add(dut):
    """Test addition: 10 + 20 = 30."""
    dut.a.value = 10
    dut.b.value = 20
    dut.op.value = 0
    await Timer(1, units="ns")
    assert dut.result.value == 30

@cocotb.test()
async def test_sub(dut):
    """Test subtraction: 30 - 10 = 20."""
    dut.a.value = 30
    dut.b.value = 10
    dut.op.value = 1
    await Timer(1, units="ns")
    assert dut.result.value == 20

@cocotb.test()
async def test_overflow(dut):
    """Test addition overflow: 255 + 1 = 256 (9 bits)."""
    dut.a.value = 255
    dut.b.value = 1
    dut.op.value = 0
    await Timer(1, units="ns")
    assert dut.result.value == 256
