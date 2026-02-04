import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_reset(dut):
    """D-FF should output 0 after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.d.value = 1
    await ClockCycles(dut.clk, 3)
    assert dut.q.value == 0

@cocotb.test()
async def test_capture(dut):
    """D-FF should capture input on rising clock edge."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    dut.d.value = 1
    await ClockCycles(dut.clk, 2)
    assert dut.q.value == 1
