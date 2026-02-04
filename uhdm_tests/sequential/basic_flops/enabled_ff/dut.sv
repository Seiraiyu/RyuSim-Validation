// IEEE 1800-2023 Section 9.4.2 - Sequential logic with clock enable
module enabled_ff (
    input  logic       clk,
    input  logic       rst,
    input  logic       en,
    input  logic [7:0] d,
    output logic [7:0] q
);
    always_ff @(posedge clk) begin
        if (rst)
            q <= 8'd0;
        else if (en)
            q <= d;
    end
endmodule
