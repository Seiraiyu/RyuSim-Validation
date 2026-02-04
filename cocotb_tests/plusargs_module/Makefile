# plusargs_module — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = tb_top
MODULE = cocotb.test_plusargs_module

include $(shell cocotb-config --makefiles)/Makefile.sim
