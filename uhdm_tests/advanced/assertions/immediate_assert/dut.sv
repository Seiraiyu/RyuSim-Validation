// IEEE 1800-2023 Section 16.3 - Immediate assertions
module immediate_assert (
    input  logic [7:0] a, b,
    output logic [8:0] sum
);
    assign sum = a + b;
endmodule
