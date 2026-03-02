"""Cocotb testbench for the RTLMeter Example design.

The Example design is a synthesizable counter that counts from 0 to 1,000,000,
asserting a milestone flag every 200,000 cycles and a done flag at 1,000,000.
The counter freezes once done is asserted.

These tests validate the full RTL intent:
  1. Reset clears counter and de-asserts milestone/done
  2. Counter increments each clock cycle
  3. Milestone asserts at every 200,000 boundary (and only there)
  4. Done asserts at exactly 1,000,000
  5. Counter freezes at 1,000,000 (no further increments)
  6. Reset mid-count restores counter to 0

IEEE 1800-2023 VPI Scheduling (Section 36.4.4):
    VPI value deposits occur in the cbReadWriteSynch region, which is part of
    the Reactive region set.  The Active region (always_ff evaluation) executes
    BEFORE the Reactive region in any given time step.  Therefore:

    1. cocotb deposits rst_n=1 via cbReadWriteSynch
    2. On the NEXT rising clock edge, always_ff sees rst_n=1 and increments cnt
    3. The RisingEdge callback fires BEFORE that edge's eval completes
    4. So the observed value at RisingEdge is the PRE-eval (previous cycle) value

    This means after reset release + one RisingEdge, cnt=0 (not 1).
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


MILESTONE_INTERVAL = 200_000
DONE_COUNT = 1_000_000
PROGRESS_INTERVAL = 1_000  # print a heartbeat every 100k cycles


async def reset_dut(dut):
    """Apply active-low reset for 5 clock cycles.

    IEEE 1800-2023 scheduling: rst_n=1 is deposited in cbReadWriteSynch.
    The following RisingEdge callback fires before eval, so the test
    observes the pre-eval state.  After this function returns, cnt=0.
    """
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_reset(dut):
    """Counter, milestone, and done should all be 0 after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    assert int(dut.cnt.value) == 0, \
        f"Counter should be 0 after reset, got {int(dut.cnt.value)}"
    assert int(dut.milestone.value) == 0, \
        "Milestone flag should be de-asserted after reset"
    assert int(dut.done.value) == 0, \
        "Done flag should be de-asserted after reset"


@cocotb.test()
async def test_counter_increments(dut):
    """Counter should increment on each rising clock edge after reset.

    Per IEEE 1800-2023: each RisingEdge observation sees the result of
    the PREVIOUS edge's always_ff evaluation (pre-eval semantics).
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    for expected in range(1, 11):
        await RisingEdge(dut.clk)
        actual = int(dut.cnt.value)
        assert actual == expected, \
            f"Expected cnt={expected}, got {actual}"


@cocotb.test()
async def test_milestone_not_asserted_early(dut):
    """Milestone should be 0 for counter values that are not multiples of 200,000."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    # Run 100 cycles — nowhere near a 200k boundary
    await ClockCycles(dut.clk, 100)

    assert int(dut.cnt.value) == 100
    assert int(dut.milestone.value) == 0, \
        f"Milestone should be 0 at cnt=100, got {int(dut.milestone.value)}"
    assert int(dut.done.value) == 0


@cocotb.test()
async def test_first_milestone(dut):
    """Milestone should assert when counter reaches 200,000."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    # Advance to cnt=199,999 (one before milestone), with progress prints
    remaining = MILESTONE_INTERVAL - 1
    elapsed = 0
    while remaining > 0:
        chunk = min(PROGRESS_INTERVAL, remaining)
        dut._log.info("chunk=%d", chunk)
        await ClockCycles(dut.clk, chunk)
        remaining -= chunk
        elapsed += chunk
        dut._log.info("cnt=%d / %d", elapsed, MILESTONE_INTERVAL)
    assert int(dut.cnt.value) == MILESTONE_INTERVAL - 1, \
        f"Expected cnt={MILESTONE_INTERVAL - 1}, got {int(dut.cnt.value)}"
    assert int(dut.milestone.value) == 0, \
        "Milestone should not be asserted one cycle before boundary"

    # One more edge → cnt=200,000
    await RisingEdge(dut.clk)
    assert int(dut.cnt.value) == MILESTONE_INTERVAL, \
        f"Expected cnt={MILESTONE_INTERVAL}, got {int(dut.cnt.value)}"
    assert int(dut.milestone.value) == 1, \
        f"Milestone should assert at cnt={MILESTONE_INTERVAL}"

    # One more edge → cnt=200,001, milestone should de-assert
    await RisingEdge(dut.clk)
    assert int(dut.cnt.value) == MILESTONE_INTERVAL + 1
    assert int(dut.milestone.value) == 0, \
        "Milestone should de-assert one cycle after boundary"


@cocotb.test()
async def test_all_milestones_and_done(dut):
    """Run the full 1,000,000 cycles: verify all 5 milestones and the done flag.

    Milestones occur at cnt = 200k, 400k, 600k, 800k, 1000k (= done).
    The milestone at cnt=1,000,000 coincides with done.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    milestones_seen = 0
    total_elapsed = 0

    for target in range(MILESTONE_INTERVAL, DONE_COUNT + 1, MILESTONE_INTERVAL):
        # Advance to next milestone in chunks, printing progress
        remaining = MILESTONE_INTERVAL
        while remaining > 0:
            chunk = min(PROGRESS_INTERVAL, remaining)
            await ClockCycles(dut.clk, chunk)
            remaining -= chunk
            total_elapsed += chunk
            dut._log.info("cnt=%d / %d", total_elapsed, DONE_COUNT)

        actual_cnt = int(dut.cnt.value)
        assert actual_cnt == target, \
            f"Expected cnt={target}, got {actual_cnt}"
        assert int(dut.milestone.value) == 1, \
            f"Milestone should be asserted at cnt={target}"

        milestones_seen += 1
        dut._log.info("milestone %d/5 reached at cnt=%d", milestones_seen, target)

    assert milestones_seen == 5, \
        f"Expected 5 milestones, saw {milestones_seen}"

    # At cnt=1,000,000, done should also be asserted
    assert int(dut.done.value) == 1, \
        f"Done flag should be asserted at cnt={DONE_COUNT}"


@cocotb.test()
async def test_counter_freezes_at_done(dut):
    """Counter should stop incrementing once done is asserted at 1,000,000."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    # Run to done
    await ClockCycles(dut.clk, DONE_COUNT)
    assert int(dut.cnt.value) == DONE_COUNT
    assert int(dut.done.value) == 1

    # Run 10 more cycles — counter should stay frozen
    for _ in range(10):
        await RisingEdge(dut.clk)
        assert int(dut.cnt.value) == DONE_COUNT, \
            f"Counter should be frozen at {DONE_COUNT}, got {int(dut.cnt.value)}"
        assert int(dut.done.value) == 1, \
            "Done flag should remain asserted"


@cocotb.test()
async def test_reset_mid_count(dut):
    """Applying reset mid-count should bring counter back to 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    # Count up to 500
    await ClockCycles(dut.clk, 500)
    assert int(dut.cnt.value) == 500

    # Assert reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)

    assert int(dut.cnt.value) == 0, \
        f"Counter should be 0 during reset, got {int(dut.cnt.value)}"
    assert int(dut.milestone.value) == 0
    assert int(dut.done.value) == 0

    # Release reset and verify counting resumes from 0
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    assert int(dut.cnt.value) == 0

    # Verify it starts counting again
    for expected in range(1, 6):
        await RisingEdge(dut.clk)
        assert int(dut.cnt.value) == expected, \
            f"After re-reset, expected cnt={expected}, got {int(dut.cnt.value)}"
