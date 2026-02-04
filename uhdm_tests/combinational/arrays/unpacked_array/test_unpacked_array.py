import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge


@cocotb.test()
async def test_write_and_read(dut):
    """Write 0xAA to address 0, then read it back."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.wr_en.value = 1
    dut.wr_addr.value = 0
    dut.wr_data.value = 0xAA
    dut.rd_addr.value = 0
    await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 1)

    dut.wr_en.value = 0
    dut.rd_addr.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.rd_data.value == 0xAA


@cocotb.test()
async def test_multiple_addresses(dut):
    """Write different values to addresses 0-3, read all back."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    values = [0x11, 0x22, 0x33, 0x44]
    for addr, val in enumerate(values):
        dut.wr_en.value = 1
        dut.wr_addr.value = addr
        dut.wr_data.value = val
        await RisingEdge(dut.clk)
        await ClockCycles(dut.clk, 1)

    dut.wr_en.value = 0
    for addr, expected in enumerate(values):
        dut.rd_addr.value = addr
        await ClockCycles(dut.clk, 1)
        assert dut.rd_data.value == expected
