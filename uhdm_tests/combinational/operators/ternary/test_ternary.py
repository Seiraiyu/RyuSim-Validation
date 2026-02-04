import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_ternary_sel0(dut):
    """Test ternary: sel=0 selects a."""
    dut.a.value = 0x11
    dut.b.value = 0x22
    dut.c.value = 0x33
    dut.sel.value = 0
    await Timer(1, units="ns")
    assert dut.out.value == 0x11


@cocotb.test()
async def test_ternary_sel1(dut):
    """Test ternary: sel=1 selects b."""
    dut.a.value = 0x11
    dut.b.value = 0x22
    dut.c.value = 0x33
    dut.sel.value = 1
    await Timer(1, units="ns")
    assert dut.out.value == 0x22


@cocotb.test()
async def test_ternary_sel2(dut):
    """Test ternary: sel=2 selects c."""
    dut.a.value = 0x11
    dut.b.value = 0x22
    dut.c.value = 0x33
    dut.sel.value = 2
    await Timer(1, units="ns")
    assert dut.out.value == 0x33


@cocotb.test()
async def test_ternary_sel3(dut):
    """Test ternary: sel=3 selects c (default)."""
    dut.a.value = 0x11
    dut.b.value = 0x22
    dut.c.value = 0x33
    dut.sel.value = 3
    await Timer(1, units="ns")
    assert dut.out.value == 0x33
