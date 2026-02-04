import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_comparison_equal(dut):
    """Test comparison operators with a=5, b=5 (equal values)."""
    dut.a.value = 5
    dut.b.value = 5
    await Timer(1, units="ns")
    assert dut.eq.value == 1
    assert dut.neq.value == 0
    assert dut.lt.value == 0
    assert dut.gt.value == 0
    assert dut.lte.value == 1
    assert dut.gte.value == 1


@cocotb.test()
async def test_comparison_less_than(dut):
    """Test comparison operators with a=3, b=7 (a less than b)."""
    dut.a.value = 3
    dut.b.value = 7
    await Timer(1, units="ns")
    assert dut.eq.value == 0
    assert dut.neq.value == 1
    assert dut.lt.value == 1
    assert dut.gt.value == 0
    assert dut.lte.value == 1
    assert dut.gte.value == 0


@cocotb.test()
async def test_comparison_greater_than(dut):
    """Test comparison operators with a=10, b=2 (a greater than b)."""
    dut.a.value = 10
    dut.b.value = 2
    await Timer(1, units="ns")
    assert dut.eq.value == 0
    assert dut.neq.value == 1
    assert dut.lt.value == 0
    assert dut.gt.value == 1
    assert dut.lte.value == 0
    assert dut.gte.value == 1
