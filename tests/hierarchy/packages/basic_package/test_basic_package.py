import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_magic_value(dut):
    """Test package constant: data_in=0xAB -> data_out=0xAB, is_magic=1."""
    dut.data_in.value = 0xAB
    await Timer(1, units="ns")
    assert dut.data_out.value == 0xAB
    assert dut.is_magic.value == 1


@cocotb.test()
async def test_non_magic_value(dut):
    """Test non-magic value: data_in=0x00 -> data_out=0x00, is_magic=0."""
    dut.data_in.value = 0x00
    await Timer(1, units="ns")
    assert dut.data_out.value == 0x00
    assert dut.is_magic.value == 0
