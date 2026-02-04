# array_module — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = array_module
MODULE = cocotb.test_array_module

include $(shell cocotb-config --makefiles)/Makefile.sim
