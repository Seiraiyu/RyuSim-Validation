# XuanTie-E902 -- cocotb testbench
#
# T-Head XuanTie E902 tiny RISC-V RV32EMC embedded core
# Top module: soc -- SoC wrapper containing the E902 CPU core (openE902),
# AHB bus, memory controller, and peripherals (UART, GPIO, timer, CLIC)
#
# The upstream tb.v, mnt.v, and uart_mnt.v are non-synthesizable testbench and
# monitoring modules that use initial blocks, $fopen, $display, $finish, and other
# constructs. For RyuSim, the cocotb testbench replaces these entirely.

TOPLEVEL_LANG = verilog
SIM = ryusim

# All RTL sources (header files are picked up via include directory)
VERILOG_SOURCES = $(wildcard rtl/*.v)

# Include path for configuration headers (cpu_cfig.h)
VERILOG_INCLUDE_DIRS = rtl

TOPLEVEL = soc
MODULE = test_xuantie_e902

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
