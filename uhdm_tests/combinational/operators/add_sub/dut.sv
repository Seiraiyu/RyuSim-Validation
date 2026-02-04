// IEEE 1800-2023 Section 11.4.3 - Arithmetic operators
module add_sub (
    input  logic [7:0] a, b,
    input  logic       op,  // 0=add, 1=sub
    output logic [8:0] result
);
    assign result = op ? (a - b) : (a + b);
endmodule
