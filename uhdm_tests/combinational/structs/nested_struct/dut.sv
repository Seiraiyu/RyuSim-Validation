// IEEE 1800-2023 Section 7.2.1 - Nested packed structures
module nested_struct (
    input  logic [23:0] raw,
    output logic [7:0]  inner_x,
    output logic [7:0]  inner_y,
    output logic [7:0]  outer_z
);
    typedef struct packed {
        logic [7:0] x;
        logic [7:0] y;
    } inner_t;

    typedef struct packed {
        inner_t inner;
        logic [7:0] z;
    } outer_t;

    outer_t s;
    assign s = raw;
    assign inner_x = s.inner.x;
    assign inner_y = s.inner.y;
    assign outer_z = s.z;
endmodule
