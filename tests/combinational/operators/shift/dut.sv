// IEEE 1800-2023 Section 11.4.10 - Shift operators
module shift (
    input  logic signed [7:0] a,
    input  logic [2:0] amt,
    output logic [7:0] lsl_out, lsr_out,
    output logic signed [7:0] asr_out
);
    assign lsl_out = a << amt;
    assign lsr_out = a >> amt;
    assign asr_out = a >>> amt;
endmodule
