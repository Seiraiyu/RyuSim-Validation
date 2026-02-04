// IEEE 1800-2023 Section 7.2.1 - Packed structures
module packed_struct (
    input  logic [15:0] raw,
    output logic [7:0]  field_a,
    output logic [7:0]  field_b
);
    typedef struct packed {
        logic [7:0] a;
        logic [7:0] b;
    } my_struct_t;

    my_struct_t s;
    assign s = raw;
    assign field_a = s.a;
    assign field_b = s.b;
endmodule
