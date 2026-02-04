import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_shift_positive(dut):
    """Test shift operators with positive value a=0x05, amt=2."""
    dut.a.value = 0x05
    dut.amt.value = 2
    await Timer(1, units="ns")
    assert dut.lsl_out.value == 0x14
    assert dut.lsr_out.value == 0x01


@cocotb.test()
async def test_shift_arithmetic_negative(dut):
    """Test arithmetic right shift with negative value a=0x80, amt=2."""
    dut.a.value = 0x80
    dut.amt.value = 2
    await Timer(1, units="ns")
    assert dut.asr_out.value == 0xE0
