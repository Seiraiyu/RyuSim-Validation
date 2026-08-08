// Stub for the include rtlmeter's harness injects at the end of tb_top.sv.
// Upstream generates this to instantiate __rtlmeter_utils (cycle counting,
// +max_cycles, +trace plusargs) — harness features our Makefile replaces.
// Empty on purpose so the vendored tb_top.sv stays byte-identical to
// verilator/rtlmeter@a9180d6c.
