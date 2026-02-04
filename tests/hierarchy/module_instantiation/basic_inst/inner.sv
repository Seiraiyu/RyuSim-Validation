// IEEE 1800-2023 Section 23.3.2 - Module instantiation
module inner (
    input  logic [7:0] a,
    output logic [7:0] b
);
    assign b = a + 8'd1;
endmodule
