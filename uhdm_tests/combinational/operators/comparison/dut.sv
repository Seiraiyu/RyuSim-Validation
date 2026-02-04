// IEEE 1800-2023 Section 11.4.4 - Comparison operators
module comparison (
    input  logic [7:0] a, b,
    output logic       eq, neq, lt, gt, lte, gte
);
    assign eq  = (a == b);
    assign neq = (a != b);
    assign lt  = (a < b);
    assign gt  = (a > b);
    assign lte = (a <= b);
    assign gte = (a >= b);
endmodule
