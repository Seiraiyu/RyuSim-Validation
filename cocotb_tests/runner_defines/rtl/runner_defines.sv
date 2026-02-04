// Ported for RyuSim from upstream cocotb runner_defines design.
// The upstream runner_defines.sv was empty (0 bytes). This is a
// minimal synthesizable placeholder that provides a simple
// parameterized module to exercise compilation and simulation.

module runner_defines #(
    parameter WIDTH = 8,
    parameter DEPTH = 4
) (
    input  logic              clk,
    input  logic              reset,
    input  logic [WIDTH-1:0]  data_in,
    output logic [WIDTH-1:0]  data_out
);

// Simple shift register of configurable depth
logic [WIDTH-1:0] pipeline [0:DEPTH-1];

always_ff @(posedge clk or posedge reset) begin
    if (reset) begin
        for (int i = 0; i < DEPTH; i++)
            pipeline[i] <= '0;
    end else begin
        pipeline[0] <= data_in;
        for (int i = 1; i < DEPTH; i++)
            pipeline[i] <= pipeline[i-1];
    end
end

assign data_out = pipeline[DEPTH-1];

endmodule
