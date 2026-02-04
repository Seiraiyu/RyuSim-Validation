# VeeR-EH2 — cocotb testbench
#
# Western Digital VeeR EH2 RISC-V core (CHIPS Alliance)
# Top module: eh2_veer_wrapper — wraps eh2_veer + eh2_mem + dmi_wrapper
#
# The upstream tb_top.sv is a Verilator-specific testbench that uses $readmemh,
# initial blocks, and other non-synthesizable constructs. For RyuSim, the cocotb
# testbench replaces tb_top entirely: it drives clock, reset, and AXI memory
# interfaces from Python.
#
# Configuration: the default VeeR EH2 config is used. Include files in rtl/default/
# provide the configuration parameters (common_defines.vh, eh2_param.vh, eh2_pdef.vh).
#
# Note: VeeR EH2 is a dual-threaded core. Unlike EH1 and EL2, it supports
# hardware multi-threading with 2 hardware threads. Control signals like
# halt/run/interrupt have per-thread instances. It uses the eh2_pkg package
# and pt.* parameter struct.

TOPLEVEL_LANG = verilog
SIM = ryusim

# Core RTL sources — order follows upstream descriptor.yaml
# Excludes tb_top.sv (replaced by cocotb)
# dasm.svi is an include file per upstream
VERILOG_SOURCES = \
    rtl/eh2_def.sv \
    rtl/eh2_veer_wrapper.sv \
    rtl/eh2_mem.sv \
    rtl/eh2_pic_ctrl.sv \
    rtl/eh2_veer.sv \
    rtl/eh2_dma_ctrl.sv \
    rtl/eh2_ifu_aln_ctl.sv \
    rtl/eh2_ifu_compress_ctl.sv \
    rtl/eh2_ifu_ifc_ctl.sv \
    rtl/eh2_ifu_bp_ctl.sv \
    rtl/eh2_ifu_ic_mem.sv \
    rtl/eh2_ifu_mem_ctl.sv \
    rtl/eh2_ifu_iccm_mem.sv \
    rtl/eh2_ifu_btb_mem.sv \
    rtl/eh2_ifu.sv \
    rtl/eh2_dec_decode_ctl.sv \
    rtl/eh2_dec_gpr_ctl.sv \
    rtl/eh2_dec_ib_ctl.sv \
    rtl/eh2_dec_tlu_ctl.sv \
    rtl/eh2_dec_tlu_top.sv \
    rtl/eh2_dec_csr.sv \
    rtl/eh2_dec_trigger.sv \
    rtl/eh2_dec.sv \
    rtl/eh2_exu_alu_ctl.sv \
    rtl/eh2_exu_mul_ctl.sv \
    rtl/eh2_exu_div_ctl.sv \
    rtl/eh2_exu.sv \
    rtl/eh2_lsu.sv \
    rtl/eh2_lsu_clkdomain.sv \
    rtl/eh2_lsu_addrcheck.sv \
    rtl/eh2_lsu_lsc_ctl.sv \
    rtl/eh2_lsu_stbuf.sv \
    rtl/eh2_lsu_bus_buffer.sv \
    rtl/eh2_lsu_bus_intf.sv \
    rtl/eh2_lsu_ecc.sv \
    rtl/eh2_lsu_dccm_mem.sv \
    rtl/eh2_lsu_dccm_ctl.sv \
    rtl/eh2_lsu_trigger.sv \
    rtl/eh2_lsu_amo.sv \
    rtl/eh2_dbg.sv \
    rtl/dmi_wrapper.v \
    rtl/dmi_jtag_to_core_sync.v \
    rtl/rvjtag_tap.v \
    rtl/eh2_lib.sv \
    rtl/beh_lib.sv \
    rtl/mem_lib.sv \
    rtl/axi_lsu_dma_bridge.sv \
    rtl/ahb_sif.sv

# Include path for configuration headers (default config)
VERILOG_INCLUDE_DIRS = rtl/default

TOPLEVEL = eh2_veer_wrapper
MODULE = cocotb.test_veer_eh2

include $(shell cocotb-config --makefiles)/Makefile.sim
