# basic_hierarchy_module — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = basic_hierarchy_module
MODULE = test_basic_hierarchy_module

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
