# VeeR-EL2 — native testbench (upstream rtlmeter tb_top) under RyuSim.
#
# tb_top $readmemh's "program.hex" from the cwd, so each test runs in
# work/<test>/ with its program staged; iteration counts come from upstream
# rtlmeter descriptor.yaml (default configuration).
SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

TB_TOP = tb_top
SIM_BIN = obj_dir/build/$(TB_TOP)_sim
PASS_MARKER = TEST_PASSED

# Upstream descriptor.yaml compile order (src/ -> rtl/), TB last.
RTL_SOURCES = \
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

TB_SOURCES = tb/tb_top_pkg.sv tb/tb_top.sv

# Flag spellings verified against `ryusim compile --help` in Task 1.
# -Itb resolves __rtlmeter_top_include.vh (stubbed; see tb/).
# --no-x-init matches the rtlmeter reference semantics (Verilator is
# 2-state/zero-init); under IEEE X-init the hello run does not complete
# in >40 min vs ~5 s zero-init — tracked upstream (RyuSimAlt X-init issue).
RYUSIM_FLAGS = --top $(TB_TOP) -Irtl -Irtl/default -Itb --jobs 4 --no-x-init

# Per-test plusargs — upstream descriptor.yaml, default configuration.
ARGS_hello =
ARGS_dhrystone = +iterations=17500
ARGS_coremark = +iterations=14
ARGS_coremark_iccm = +iterations=22

PROGRAM_hello = hello.hex
PROGRAM_dhrystone = dhrystone.hex
PROGRAM_coremark = coremark.hex
PROGRAM_coremark_iccm = coremark_iccm.hex

compile: $(SIM_BIN)

$(SIM_BIN): $(RTL_SOURCES) $(TB_SOURCES)
	ryusim compile $(RTL_SOURCES) $(TB_SOURCES) $(RYUSIM_FLAGS)

test-%: compile
	mkdir -p work/$*
	cp programs/$(PROGRAM_$*) work/$*/program.hex
	cd work/$* && ../../$(SIM_BIN) $(ARGS_$*) 2>&1 | tee run.log
	grep -q "$(PASS_MARKER)" work/$*/run.log

all: test-hello test-dhrystone test-coremark test-coremark_iccm

clean:
	rm -rf obj_dir work

.PHONY: compile all clean
.DEFAULT_GOAL := all
