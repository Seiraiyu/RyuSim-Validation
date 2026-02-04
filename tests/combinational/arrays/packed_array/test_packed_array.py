import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_select_byte0(dut):
    """Select byte 0 from packed array: 0xAABBCCDD[0] = 0xDD."""
    dut.data_in.value = 0xAABBCCDD
    dut.sel.value = 0
    await Timer(1, units="ns")
    assert dut.data_out.value == 0xDD


@cocotb.test()
async def test_select_byte2(dut):
    """Select byte 2 from packed array: 0xAABBCCDD[2] = 0xBB."""
    dut.data_in.value = 0xAABBCCDD
    dut.sel.value = 2
    await Timer(1, units="ns")
    assert dut.data_out.value == 0xBB


@cocotb.test()
async def test_select_byte3(dut):
    """Select byte 3 from packed array: 0xAABBCCDD[3] = 0xAA."""
    dut.data_in.value = 0xAABBCCDD
    dut.sel.value = 3
    await Timer(1, units="ns")
    assert dut.data_out.value == 0xAA
