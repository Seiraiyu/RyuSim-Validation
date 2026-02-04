import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_default_params(dut):
    """Test with default parameters (WIDTH=8, INIT=0): a=42 -> b=42."""
    dut.a.value = 42
    await Timer(1, units="ns")
    assert dut.b.value == 42


@cocotb.test()
async def test_max_value(dut):
    """Test with default parameters: a=255 -> b=255."""
    dut.a.value = 255
    await Timer(1, units="ns")
    assert dut.b.value == 255
