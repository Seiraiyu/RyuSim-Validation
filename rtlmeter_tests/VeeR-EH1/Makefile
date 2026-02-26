# VeeR-EH1 — cocotb testbench
#
# Western Digital VeeR EH1 RISC-V core (CHIPS Alliance)
# Top module: veer_wrapper — wraps veer + mem + dmi_wrapper
#
# The upstream tb_top.sv is a Verilator-specific testbench that uses $readmemh,
# initial blocks, and other non-synthesizable constructs. For RyuSim, the cocotb
# testbench replaces tb_top entirely: it drives clock, reset, and AXI memory
# interfaces from Python.
#
# Configuration: the default VeeR config is used. Include files in rtl/default/
# provide the configuration parameters (common_defines.vh, pic_map_auto.h).
#
# Note: VeeR EH1 is the first-generation core. Unlike EL2, it uses the
# veer_types package (not el2_pkg) and `RV_*` preprocessor macros for bus widths.

TOPLEVEL_LANG = verilog
SIM = ryusim

# Core RTL sources — order follows upstream descriptor.yaml
# Excludes tb_top.sv (replaced by cocotb) and ahb_sif.sv (testbench memory)
# axi_lsu_dma_bridge.sv, dasm.svi, and global.h are include files per upstream
VERILOG_SOURCES = \
    rtl/veer_types.sv \
    rtl/veer_wrapper.sv \
    rtl/mem.sv \
    rtl/pic_ctrl.sv \
    rtl/veer.sv \
    rtl/dma_ctrl.sv \
    rtl/ifu_aln_ctl.sv \
    rtl/ifu_compress_ctl.sv \
    rtl/ifu_ifc_ctl.sv \
    rtl/ifu_bp_ctl.sv \
    rtl/ifu_ic_mem.sv \
    rtl/ifu_mem_ctl.sv \
    rtl/ifu_iccm_mem.sv \
    rtl/ifu.sv \
    rtl/dec_decode_ctl.sv \
    rtl/dec_gpr_ctl.sv \
    rtl/dec_ib_ctl.sv \
    rtl/dec_tlu_ctl.sv \
    rtl/dec_trigger.sv \
    rtl/dec.sv \
    rtl/exu_alu_ctl.sv \
    rtl/exu_mul_ctl.sv \
    rtl/exu_div_ctl.sv \
    rtl/exu.sv \
    rtl/lsu.sv \
    rtl/lsu_clkdomain.sv \
    rtl/lsu_addrcheck.sv \
    rtl/lsu_lsc_ctl.sv \
    rtl/lsu_stbuf.sv \
    rtl/lsu_bus_buffer.sv \
    rtl/lsu_bus_intf.sv \
    rtl/lsu_ecc.sv \
    rtl/lsu_dccm_mem.sv \
    rtl/lsu_dccm_ctl.sv \
    rtl/lsu_trigger.sv \
    rtl/dbg.sv \
    rtl/dmi_wrapper.v \
    rtl/dmi_jtag_to_core_sync.v \
    rtl/rvjtag_tap.sv \
    rtl/beh_lib.sv \
    rtl/mem_lib.sv \
    rtl/ahb_sif.sv

# Include path for configuration headers (default config)
VERILOG_INCLUDE_DIRS = rtl/default

TOPLEVEL = veer_wrapper
MODULE = test_veer_eh1

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
