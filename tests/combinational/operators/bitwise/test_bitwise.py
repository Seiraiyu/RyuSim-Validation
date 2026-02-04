import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_bitwise_aa_55(dut):
    """Test bitwise operators with a=0xAA, b=0x55."""
    dut.a.value = 0xAA
    dut.b.value = 0x55
    await Timer(1, units="ns")
    assert dut.and_out.value == 0x00
    assert dut.or_out.value == 0xFF
    assert dut.xor_out.value == 0xFF
    assert dut.not_out.value == 0x55


@cocotb.test()
async def test_bitwise_ff_0f(dut):
    """Test bitwise operators with a=0xFF, b=0x0F."""
    dut.a.value = 0xFF
    dut.b.value = 0x0F
    await Timer(1, units="ns")
    assert dut.and_out.value == 0x0F
    assert dut.or_out.value == 0xFF
    assert dut.xor_out.value == 0xF0
    assert dut.not_out.value == 0x00
