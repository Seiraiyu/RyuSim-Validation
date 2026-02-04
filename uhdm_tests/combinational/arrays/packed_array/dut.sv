// IEEE 1800-2023 Section 7.4.1 - Packed arrays
module packed_array (
    input  logic [3:0][7:0] data_in,
    input  logic [1:0]      sel,
    output logic [7:0]      data_out
);
    assign data_out = data_in[sel];
endmodule
