import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_write_and_read(dut):
    """Write 0xAA to address 0 and read it back."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    # Write 0xAA to address 0
    dut.wr_en.value = 1
    dut.wr_addr.value = 0
    dut.wr_data.value = 0xAA
    dut.rd_addr.value = 0
    await ClockCycles(dut.clk, 2)
    # Stop writing, read back
    dut.wr_en.value = 0
    dut.rd_addr.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.rd_data.value == 0xAA, f"Expected 0xAA, got {hex(dut.rd_data.value)}"

@cocotb.test()
async def test_multiple_addresses(dut):
    """Write different values to different addresses and read each back."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    test_data = {0: 0x11, 1: 0x22, 2: 0x33, 3: 0x44}

    # Write values to multiple addresses
    for addr, data in test_data.items():
        dut.wr_en.value = 1
        dut.wr_addr.value = addr
        dut.wr_data.value = data
        dut.rd_addr.value = 0
        await ClockCycles(dut.clk, 1)
        await RisingEdge(dut.clk)

    dut.wr_en.value = 0

    # Read back and verify each address
    for addr, expected in test_data.items():
        dut.rd_addr.value = addr
        await ClockCycles(dut.clk, 1)
        assert dut.rd_data.value == expected, \
            f"Addr {addr}: expected {hex(expected)}, got {hex(dut.rd_data.value)}"
