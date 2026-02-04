// IEEE 1800-2023 Section 6.19.5 - Enumeration methods
module enum_methods (
    input  logic [1:0] sel,
    output logic [1:0] next_val,
    output logic [1:0] first_val
);
    typedef enum logic [1:0] {
        A = 2'b00,
        B = 2'b01,
        C = 2'b10,
        D = 2'b11
    } my_enum_t;

    my_enum_t current;
    assign current = my_enum_t'(sel);
    assign next_val = (current == D) ? A : my_enum_t'(current + 1);
    assign first_val = A;
endmodule
