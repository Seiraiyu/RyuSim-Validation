# uart2bus — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = uart2bus_top
MODULE = test_uart2bus

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotbext-ryusim-config --makefiles)/Makefile.sim
