# Vortex RISC-V GPGPU — cocotb testbench
#
# Vortex is an open-source RISC-V GPGPU from Georgia Tech. The design includes
# a configurable number of clusters/cores/warps/threads with FPU support via
# the PULP fpnew unit.
#
# Top module: Vortex — the GPU top-level with memory and DCR interfaces.
# The upstream tb.sv uses initial blocks, #delays, DPI-C imports, and
# $readmemh, all replaced by the cocotb testbench.
#
# Configuration: mini (1 cluster, 1 core, 4 warps, 4 threads) for basic
# compilation and smoke testing.

TOPLEVEL_LANG = verilog
SIM = ryusim

# Source file order follows upstream descriptor.yaml
# Packages first, then design files
VERILOG_SOURCES = \
    rtl/VX_gpu_pkg.sv \
    rtl/VX_fpu_pkg.sv \
    rtl/VX_trace_pkg.sv \
    rtl/fpnew/fpnew_pkg.sv \
    rtl/fpnew/cf_math_pkg.sv \
    rtl/fpnew/defs_div_sqrt_mvp.sv \
    rtl/fpnew/control_mvp.sv \
    rtl/Vortex.sv \
    rtl/VX_dcr_bus_if.sv \
    rtl/VX_mem_bus_if.sv \
    rtl/VX_cache_wrap.sv \
    rtl/VX_cluster.sv \
    rtl/VX_pipe_register.sv \
    rtl/VX_reset_relay.sv \
    rtl/VX_cache_bypass.sv \
    rtl/VX_socket.sv \
    rtl/VX_bits_remove.sv \
    rtl/VX_cache_cluster.sv \
    rtl/VX_core.sv \
    rtl/VX_elastic_buffer.sv \
    rtl/VX_generic_arbiter.sv \
    rtl/VX_mem_arb.sv \
    rtl/VX_lsu_mem_if.sv \
    rtl/VX_bits_insert.sv \
    rtl/VX_branch_ctl_if.sv \
    rtl/VX_cache.sv \
    rtl/VX_commit.sv \
    rtl/VX_commit_csr_if.sv \
    rtl/VX_commit_if.sv \
    rtl/VX_commit_sched_if.sv \
    rtl/VX_dcr_data.sv \
    rtl/VX_decode.sv \
    rtl/VX_decode_if.sv \
    rtl/VX_decode_sched_if.sv \
    rtl/VX_dispatch_if.sv \
    rtl/VX_execute.sv \
    rtl/VX_fetch.sv \
    rtl/VX_fetch_if.sv \
    rtl/VX_issue.sv \
    rtl/VX_lmem_unit.sv \
    rtl/VX_lsu_adapter.sv \
    rtl/VX_mem_coalescer.sv \
    rtl/VX_priority_arbiter.sv \
    rtl/VX_rr_arbiter.sv \
    rtl/VX_sched_csr_if.sv \
    rtl/VX_schedule.sv \
    rtl/VX_schedule_if.sv \
    rtl/VX_skid_buffer.sv \
    rtl/VX_stream_arb.sv \
    rtl/VX_stream_switch.sv \
    rtl/VX_warp_ctl_if.sv \
    rtl/VX_writeback_if.sv \
    rtl/VX_alu_unit.sv \
    rtl/VX_cache_bank.sv \
    rtl/VX_cache_flush.sv \
    rtl/VX_dp_ram.sv \
    rtl/VX_fair_arbiter.sv \
    rtl/VX_fpu_csr_if.sv \
    rtl/VX_fpu_unit.sv \
    rtl/VX_index_buffer.sv \
    rtl/VX_issue_slice.sv \
    rtl/VX_local_mem.sv \
    rtl/VX_lsu_unit.sv \
    rtl/VX_lzc.sv \
    rtl/VX_onehot_encoder.sv \
    rtl/VX_pending_size.sv \
    rtl/VX_pipe_buffer.sv \
    rtl/VX_popcount.sv \
    rtl/VX_priority_encoder.sv \
    rtl/VX_reduce.sv \
    rtl/VX_sfu_unit.sv \
    rtl/VX_split_join.sv \
    rtl/VX_stream_buffer.sv \
    rtl/VX_stream_pack.sv \
    rtl/VX_stream_unpack.sv \
    rtl/VX_stream_xbar.sv \
    rtl/VX_execute_if.sv \
    rtl/VX_allocator.sv \
    rtl/VX_alu_int.sv \
    rtl/VX_alu_muldiv.sv \
    rtl/VX_bank_flush.sv \
    rtl/VX_cache_data.sv \
    rtl/VX_cache_mshr.sv \
    rtl/VX_cache_tags.sv \
    rtl/VX_csr_unit.sv \
    rtl/VX_dispatch_unit.sv \
    rtl/VX_fifo_queue.sv \
    rtl/VX_find_first.sv \
    rtl/VX_fpu_fpnew.sv \
    rtl/VX_gather_unit.sv \
    rtl/VX_ibuffer_if.sv \
    rtl/VX_lsu_slice.sv \
    rtl/VX_scan.sv \
    rtl/VX_sp_ram.sv \
    rtl/VX_wctl_unit.sv \
    rtl/VX_csr_data.sv \
    rtl/VX_dispatch.sv \
    rtl/VX_elastic_adapter.sv \
    rtl/VX_ibuffer.sv \
    rtl/VX_ipdom_stack.sv \
    rtl/VX_mem_scheduler.sv \
    rtl/VX_multiplier.sv \
    rtl/VX_operands.sv \
    rtl/VX_operands_if.sv \
    rtl/VX_scoreboard.sv \
    rtl/VX_scoreboard_if.sv \
    rtl/VX_serial_div.sv \
    rtl/VX_shift_register.sv \
    rtl/fpnew/fpnew_top.sv \
    rtl/fpnew/fpnew_opgroup_block.sv \
    rtl/fpnew/rr_arb_tree.sv \
    rtl/fpnew/fpnew_opgroup_fmt_slice.sv \
    rtl/fpnew/fpnew_opgroup_multifmt_slice.sv \
    rtl/fpnew/lzc.sv \
    rtl/fpnew/fpnew_cast_multi.sv \
    rtl/fpnew/fpnew_divsqrt_multi.sv \
    rtl/fpnew/fpnew_fma.sv \
    rtl/fpnew/fpnew_noncomp.sv \
    rtl/fpnew/div_sqrt_top_mvp.sv \
    rtl/fpnew/fpnew_classifier.sv \
    rtl/fpnew/fpnew_rounding.sv \
    rtl/fpnew/norm_div_sqrt_mvp.sv \
    rtl/fpnew/nrbd_nrsc_mvp.sv \
    rtl/fpnew/preprocess_mvp.sv \
    rtl/fpnew/iteration_div_sqrt_mvp.sv

# Include paths for header files
VERILOG_INCLUDE_DIRS = rtl rtl/fpnew

# Compile-time defines (mini configuration: 1 cluster, 1 core)
EXTRA_ARGS += \
    -DSIMULATION=1 \
    -DXLEN_32=1 \
    -DFPU_FPNEW=1 \
    -DNDEBUG=1 \
    -DNUM_CLUSTERS=1 \
    -DNUM_CORES=1 \
    -DNUM_WARPS=4 \
    -DNUM_THREADS=4

# Limit VPI depth to top-level ports (faster compile on CI)
EXTRA_ARGS += --vpi-depth 1

# Parallelize C++ compilation of generated simulation code
EXTRA_ARGS += --jobs 4

TOPLEVEL = Vortex
MODULE = test_vortex

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
