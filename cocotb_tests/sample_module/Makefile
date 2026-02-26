# sample_module — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = sample_module
MODULE = test_sample_module

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
