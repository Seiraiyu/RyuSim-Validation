# VeeR-EL2 — cocotb testbench
#
# Western Digital VeeR EL2 RISC-V core (CHIPS Alliance)
# Top module: veer_wrapper — wraps el2_veer_wrapper + memory interface flattening
#
# The upstream tb_top.sv is a Verilator-specific testbench that uses $readmemh,
# initial blocks, and other non-synthesizable constructs. For RyuSim, the cocotb
# testbench replaces tb_top entirely: it drives clock, reset, and AXI memory
# interfaces from Python.
#
# Configuration: the default VeeR config is used. Include files in rtl/default/
# provide the configuration parameters (common_defines.vh, el2_param.vh, etc.)

TOPLEVEL_LANG = verilog
SIM = ryusim

# Core RTL sources — order follows upstream descriptor.yaml
# Excludes tb_top.sv (replaced by cocotb) and tb_top_pkg.sv (testbench-only)
VERILOG_SOURCES = \
    rtl/el2_def.sv \
    rtl/veer_wrapper.sv \
    rtl/el2_veer_wrapper.sv \
    rtl/el2_mem.sv \
    rtl/el2_pic_ctrl.sv \
    rtl/el2_veer.sv \
    rtl/el2_dma_ctrl.sv \
    rtl/el2_pmp.sv \
    rtl/el2_ifu_aln_ctl.sv \
    rtl/el2_ifu_compress_ctl.sv \
    rtl/el2_ifu_ifc_ctl.sv \
    rtl/el2_ifu_bp_ctl.sv \
    rtl/el2_ifu_ic_mem.sv \
    rtl/el2_ifu_mem_ctl.sv \
    rtl/el2_ifu_iccm_mem.sv \
    rtl/el2_ifu.sv \
    rtl/el2_dec_decode_ctl.sv \
    rtl/el2_dec_gpr_ctl.sv \
    rtl/el2_dec_ib_ctl.sv \
    rtl/el2_dec_pmp_ctl.sv \
    rtl/el2_dec_tlu_ctl.sv \
    rtl/el2_dec_trigger.sv \
    rtl/el2_dec.sv \
    rtl/el2_exu_alu_ctl.sv \
    rtl/el2_exu_mul_ctl.sv \
    rtl/el2_exu_div_ctl.sv \
    rtl/el2_exu.sv \
    rtl/el2_lsu.sv \
    rtl/el2_lsu_clkdomain.sv \
    rtl/el2_lsu_addrcheck.sv \
    rtl/el2_lsu_lsc_ctl.sv \
    rtl/el2_lsu_stbuf.sv \
    rtl/el2_lsu_bus_buffer.sv \
    rtl/el2_lsu_bus_intf.sv \
    rtl/el2_lsu_ecc.sv \
    rtl/el2_lsu_dccm_mem.sv \
    rtl/el2_lsu_dccm_ctl.sv \
    rtl/el2_lsu_trigger.sv \
    rtl/el2_dbg.sv \
    rtl/dmi_mux.v \
    rtl/dmi_wrapper.v \
    rtl/dmi_jtag_to_core_sync.v \
    rtl/rvjtag_tap.v \
    rtl/el2_lib.sv \
    rtl/beh_lib.sv \
    rtl/mem_lib.sv \
    rtl/axi_lsu_dma_bridge.sv \
    rtl/ahb_sif.sv \
    rtl/el2_mem_if.sv

# Include path for configuration headers (default config)
VERILOG_INCLUDE_DIRS = rtl/default

TOPLEVEL = veer_wrapper
MODULE = test_veer_el2

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
