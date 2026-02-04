// IEEE 1800-2023 Section 27.5 - Conditional generate constructs
module if_generate #(
    parameter USE_ADD = 1
)(
    input  logic [7:0] a, b,
    output logic [8:0] result
);
    generate
        if (USE_ADD) begin : gen_add
            assign result = a + b;
        end else begin : gen_sub
            assign result = a - b;
        end
    endgenerate
endmodule
