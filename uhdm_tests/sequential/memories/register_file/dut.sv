// IEEE 1800-2023 Section 7.4.2 - Unpacked array memory (register file)
module register_file #(
    parameter DEPTH = 8,
    parameter WIDTH = 8
)(
    input  logic                    clk,
    input  logic                    wr_en,
    input  logic [$clog2(DEPTH)-1:0] wr_addr, rd_addr,
    input  logic [WIDTH-1:0]        wr_data,
    output logic [WIDTH-1:0]        rd_data
);
    logic [WIDTH-1:0] mem [DEPTH];

    always_ff @(posedge clk) begin
        if (wr_en)
            mem[wr_addr] <= wr_data;
    end

    assign rd_data = mem[rd_addr];
endmodule
