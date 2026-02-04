// IEEE 1800-2023 Section 11.4.9 - Reduction operators
module reduction (
    input  logic [7:0] a,
    output logic       and_r, or_r, xor_r
);
    assign and_r = &a;
    assign or_r  = |a;
    assign xor_r = ^a;
endmodule
