// IEEE 1800-2023 Section 23.3.2 - Module instantiation
module basic_inst (
    input  logic [7:0] in_val,
    output logic [7:0] out_val
);
    inner u_inner (
        .a(in_val),
        .b(out_val)
    );
endmodule
