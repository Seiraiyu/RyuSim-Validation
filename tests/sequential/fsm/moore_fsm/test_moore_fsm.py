import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_reset_state(dut):
    """FSM should be in S0 (state_out=0) after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.in_bit.value = 0
    await ClockCycles(dut.clk, 3)
    assert dut.state_out.value == 0

@cocotb.test()
async def test_state_transitions(dut):
    """FSM should transition S0->S1->S2->S0 with in_bit=1."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    # Reset
    dut.rst.value = 1
    dut.in_bit.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0

    # S0 -> S1: drive in_bit=1
    dut.in_bit.value = 1
    await ClockCycles(dut.clk, 1)
    await RisingEdge(dut.clk)
    assert dut.state_out.value == 1, f"Expected S1 (1), got {dut.state_out.value}"

    # S1 -> S2: keep in_bit=1
    await RisingEdge(dut.clk)
    assert dut.state_out.value == 2, f"Expected S2 (2), got {dut.state_out.value}"

    # S2 -> S0: unconditional
    await RisingEdge(dut.clk)
    assert dut.state_out.value == 0, f"Expected S0 (0), got {dut.state_out.value}"

@cocotb.test()
async def test_stay_in_s0(dut):
    """FSM should stay in S0 when in_bit=0."""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.in_bit.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    dut.in_bit.value = 0
    await ClockCycles(dut.clk, 3)
    assert dut.state_out.value == 0
