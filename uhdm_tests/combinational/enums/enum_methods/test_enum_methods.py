import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_next_from_a(dut):
    """Test next value from A: sel=0 -> next=1, first=0."""
    dut.sel.value = 0
    await Timer(1, units="ns")
    assert dut.next_val.value == 1
    assert dut.first_val.value == 0


@cocotb.test()
async def test_next_from_b(dut):
    """Test next value from B: sel=1 -> next=2."""
    dut.sel.value = 1
    await Timer(1, units="ns")
    assert dut.next_val.value == 2


@cocotb.test()
async def test_wrap_from_d(dut):
    """Test wrap-around from D: sel=3 -> next=0."""
    dut.sel.value = 3
    await Timer(1, units="ns")
    assert dut.next_val.value == 0


@cocotb.test()
async def test_first_always_zero(dut):
    """Test that first_val is always A (0) regardless of sel."""
    for sel in range(4):
        dut.sel.value = sel
        await Timer(1, units="ns")
        assert dut.first_val.value == 0
