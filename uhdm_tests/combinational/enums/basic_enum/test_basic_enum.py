import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_idle(dut):
    """Test IDLE state: sel=0 -> out=0."""
    dut.sel.value = 0
    await Timer(1, units="ns")
    assert dut.out.value == 0


@cocotb.test()
async def test_run(dut):
    """Test RUN state: sel=1 -> out=1."""
    dut.sel.value = 1
    await Timer(1, units="ns")
    assert dut.out.value == 1


@cocotb.test()
async def test_done(dut):
    """Test DONE state: sel=2 -> out=2."""
    dut.sel.value = 2
    await Timer(1, units="ns")
    assert dut.out.value == 2


@cocotb.test()
async def test_error(dut):
    """Test ERROR state: sel=3 -> out=255."""
    dut.sel.value = 3
    await Timer(1, units="ns")
    assert dut.out.value == 255
