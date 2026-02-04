// IEEE 1800-2023 Section 23.10 - Overriding module parameters
module param_override #(
    parameter WIDTH = 8,
    parameter INIT  = 0
)(
    input  logic [WIDTH-1:0] a,
    output logic [WIDTH-1:0] b
);
    assign b = a + INIT[WIDTH-1:0];
endmodule
