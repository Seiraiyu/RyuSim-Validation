// IEEE 1800-2023 Section 26.2 - Package declarations
package my_pkg;
    typedef logic [7:0] byte_t;
    localparam byte_t MAGIC = 8'hAB;
endpackage

module basic_package (
    input  my_pkg::byte_t data_in,
    output my_pkg::byte_t data_out,
    output logic          is_magic
);
    assign data_out = data_in;
    assign is_magic = (data_in == my_pkg::MAGIC);
endmodule
