// IEEE 1800-2023 Section 7.4.2 - Unpacked arrays
module unpacked_array (
    input  logic [7:0] wr_data,
    input  logic [1:0] wr_addr, rd_addr,
    input  logic       wr_en, clk,
    output logic [7:0] rd_data
);
    logic [7:0] mem [4];

    always_ff @(posedge clk) begin
        if (wr_en)
            mem[wr_addr] <= wr_data;
    end

    assign rd_data = mem[rd_addr];
endmodule
