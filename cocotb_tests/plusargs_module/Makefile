# plusargs_module — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = tb_top
MODULE = test_plusargs_module

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
