# XuanTie-C906 -- cocotb testbench
#
# T-Head XuanTie C906 mid-range RISC-V RV64GC application core
# Top module: soc -- SoC wrapper containing the C906 CPU core, AXI interconnect,
# memory controller, and peripherals (UART, GPIO, timer, PLIC)
#
# The upstream tb.v is a Verilator-specific testbench that uses initial blocks,
# always # delays, $readmemh, and other non-synthesizable constructs. For RyuSim,
# the cocotb testbench replaces tb.v entirely.

TOPLEVEL_LANG = verilog
SIM = ryusim

# All RTL sources (header files are picked up via include directory)
VERILOG_SOURCES = $(wildcard rtl/*.v)

# Include path for configuration headers (cpu_cfig.h, etc.)
VERILOG_INCLUDE_DIRS = rtl

TOPLEVEL = soc
MODULE = test_xuantie_c906

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
