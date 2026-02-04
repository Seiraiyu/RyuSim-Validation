import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_logical_both_nonzero(dut):
    """Test logical operators with a=5, b=3 (both nonzero)."""
    dut.a.value = 5
    dut.b.value = 3
    await Timer(1, units="ns")
    assert dut.and_out.value == 1
    assert dut.or_out.value == 1
    assert dut.not_out.value == 0


@cocotb.test()
async def test_logical_both_zero(dut):
    """Test logical operators with a=0, b=0 (both zero)."""
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, units="ns")
    assert dut.and_out.value == 0
    assert dut.or_out.value == 0
    assert dut.not_out.value == 1


@cocotb.test()
async def test_logical_mixed(dut):
    """Test logical operators with a=0, b=5 (one zero, one nonzero)."""
    dut.a.value = 0
    dut.b.value = 5
    await Timer(1, units="ns")
    assert dut.and_out.value == 0
    assert dut.or_out.value == 1
    assert dut.not_out.value == 1
