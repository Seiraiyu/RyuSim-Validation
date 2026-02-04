// Ported for RyuSim from upstream cocotb plusargs_module design.
// The upstream tb_top.v was entirely non-synthesizable (initial begin,
// $value$plusargs, $display, # delays). This is a minimal synthesizable
// placeholder that provides a simple register to exercise compilation
// and basic simulation.

module tb_top (
    input  logic        clk,
    input  logic        reset,
    input  logic [7:0]  data_in,
    output logic [7:0]  data_out
);

always_ff @(posedge clk or posedge reset) begin
    if (reset)
        data_out <= 8'h00;
    else
        data_out <= data_in;
end

endmodule
