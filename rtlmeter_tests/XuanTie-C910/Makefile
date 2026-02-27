# XuanTie-C910 -- cocotb testbench
#
# T-Head XuanTie C910 high-performance RISC-V RV64GC multi-issue application core
# Top module: soc -- SoC wrapper containing the C910 CPU (rv_integration_platform),
# AXI interconnect, memory controller, and peripherals (UART, GPIO, timer, PLIC)
#
# The upstream tb.v is a Verilator-specific testbench that uses initial blocks,
# always # delays, $readmemh, and other non-synthesizable constructs. For RyuSim,
# the cocotb testbench replaces tb.v entirely.

TOPLEVEL_LANG = verilog
SIM = ryusim

# All RTL sources (header files are picked up via include directory)
VERILOG_SOURCES = $(wildcard rtl/*.v)

# Include path for configuration headers (cpu_cfig.h, sysmap.h)
VERILOG_INCLUDE_DIRS = rtl

# Limit VPI depth to top-level ports (faster compile on CI)
EXTRA_ARGS += --vpi-depth 1

# Parallelize C++ compilation of generated simulation code
EXTRA_ARGS += --jobs 4

TOPLEVEL = soc
MODULE = test_xuantie_c910

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
