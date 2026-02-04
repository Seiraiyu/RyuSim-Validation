# runner_defines — cocotb testbench
TOPLEVEL_LANG = verilog
SIM = ryusim

VERILOG_SOURCES = $(wildcard rtl/*.sv) $(wildcard rtl/*.v)
TOPLEVEL = runner_defines
MODULE = cocotb.test_runner_defines

include $(shell cocotb-config --makefiles)/Makefile.sim
