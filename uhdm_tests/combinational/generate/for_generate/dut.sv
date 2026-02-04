// IEEE 1800-2023 Section 27.4 - Loop generate constructs
module for_generate #(
    parameter WIDTH = 8
)(
    input  logic [WIDTH-1:0] a, b,
    output logic [WIDTH-1:0] result
);
    genvar i;
    generate
        for (i = 0; i < WIDTH; i++) begin : gen_xor
            assign result[i] = a[i] ^ b[i];
        end
    endgenerate
endmodule
