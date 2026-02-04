# runner — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = runner
MODULE = cocotb.test_runner

include $(shell cocotb-config --makefiles)/Makefile.sim
