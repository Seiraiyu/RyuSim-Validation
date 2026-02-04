import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_reduction_all_ones(dut):
    """Test reduction operators with a=0xFF (all ones)."""
    dut.a.value = 0xFF
    await Timer(1, units="ns")
    assert dut.and_r.value == 1
    assert dut.or_r.value == 1
    assert dut.xor_r.value == 0


@cocotb.test()
async def test_reduction_all_zeros(dut):
    """Test reduction operators with a=0x00 (all zeros)."""
    dut.a.value = 0x00
    await Timer(1, units="ns")
    assert dut.and_r.value == 0
    assert dut.or_r.value == 0
    assert dut.xor_r.value == 0


@cocotb.test()
async def test_reduction_single_bit(dut):
    """Test reduction operators with a=0x01 (single bit set)."""
    dut.a.value = 0x01
    await Timer(1, units="ns")
    assert dut.and_r.value == 0
    assert dut.or_r.value == 1
    assert dut.xor_r.value == 1
