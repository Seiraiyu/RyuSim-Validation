import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer

@cocotb.test()
async def test_async_reset(dut):
    """Async reset should clear output without needing a clock edge."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst_n.value = 0
    dut.d.value = 1
    await Timer(5, units="ns")
    assert dut.q.value == 0

@cocotb.test()
async def test_capture_after_reset(dut):
    """D-FF should capture input after async reset is released."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst_n.value = 0
    dut.d.value = 0
    await ClockCycles(dut.clk, 2)
    assert dut.q.value == 0
    dut.rst_n.value = 1
    dut.d.value = 1
    await ClockCycles(dut.clk, 2)
    assert dut.q.value == 1
