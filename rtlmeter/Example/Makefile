# Example — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = top
MODULE = cocotb.test_example

include $(shell cocotb-config --makefiles)/Makefile.sim
