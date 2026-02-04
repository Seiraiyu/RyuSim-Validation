// IEEE 1800-2023 Section 11.4.11 - Conditional (ternary) operator
module ternary (
    input  logic [7:0] a, b, c,
    input  logic [1:0] sel,
    output logic [7:0] out
);
    assign out = (sel == 2'b00) ? a :
                 (sel == 2'b01) ? b : c;
endmodule
