// IEEE 1800-2023 Section 6.18 - User-defined types
module basic_typedef (
    input  logic [15:0] raw,
    output logic [7:0]  high, low
);
    typedef logic [7:0] byte_t;
    byte_t h, l;
    assign {h, l} = raw;
    assign high = h;
    assign low = l;
endmodule
