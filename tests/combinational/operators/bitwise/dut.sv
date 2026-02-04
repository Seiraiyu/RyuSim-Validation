// IEEE 1800-2023 Section 11.4.5 - Bitwise operators
module bitwise (
    input  logic [7:0] a, b,
    output logic [7:0] and_out, or_out, xor_out, not_out
);
    assign and_out = a & b;
    assign or_out  = a | b;
    assign xor_out = a ^ b;
    assign not_out = ~a;
endmodule
