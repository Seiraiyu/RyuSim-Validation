# multi_dimension_array — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = cocotb_array
MODULE = test_multi_dimension_array

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
