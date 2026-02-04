import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_reset(dut):
    """Enabled FF should output 0 after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.en.value = 1
    dut.d.value = 0xFF
    await ClockCycles(dut.clk, 3)
    assert dut.q.value == 0

@cocotb.test()
async def test_capture_when_enabled(dut):
    """Enabled FF should capture input when en=1."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.en.value = 0
    dut.d.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    dut.en.value = 1
    dut.d.value = 0xAB
    await ClockCycles(dut.clk, 2)
    assert dut.q.value == 0xAB

@cocotb.test()
async def test_hold_when_disabled(dut):
    """Enabled FF should hold value when en=0."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.en.value = 0
    dut.d.value = 0
    await ClockCycles(dut.clk, 2)
    # Load a value first
    dut.rst.value = 0
    dut.en.value = 1
    dut.d.value = 0x42
    await ClockCycles(dut.clk, 2)
    assert dut.q.value == 0x42
    # Disable and change d - q should hold
    dut.en.value = 0
    dut.d.value = 0xFF
    await ClockCycles(dut.clk, 3)
    assert dut.q.value == 0x42
