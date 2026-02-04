import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_xor_alternating(dut):
    """Test XOR with alternating bits: 0xAA ^ 0x55 = 0xFF."""
    dut.a.value = 0xAA
    dut.b.value = 0x55
    await Timer(1, units="ns")
    assert dut.result.value == 0xFF


@cocotb.test()
async def test_xor_same(dut):
    """Test XOR with identical inputs: 0xFF ^ 0xFF = 0x00."""
    dut.a.value = 0xFF
    dut.b.value = 0xFF
    await Timer(1, units="ns")
    assert dut.result.value == 0x00


@cocotb.test()
async def test_xor_zeros(dut):
    """Test XOR with zeros: 0x00 ^ 0x00 = 0x00."""
    dut.a.value = 0x00
    dut.b.value = 0x00
    await Timer(1, units="ns")
    assert dut.result.value == 0x00
