// Macros the DUT consumes but upstream defines in its excluded testbench
// (rtlmeter designs/XuanTie-C910/src/tb.v @ a9180d6c, line 53).
// cpu_sub_system_axi.v uses `APB_BASE_ADDR for pad_cpu_apb_base.
`define APB_BASE_ADDR       40'hb0000000
