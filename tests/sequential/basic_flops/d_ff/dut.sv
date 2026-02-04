// IEEE 1800-2023 Section 9.4.2 - Sequential logic (always_ff)
module d_ff (
    input  logic clk,
    input  logic rst,
    input  logic d,
    output logic q
);
    always_ff @(posedge clk) begin
        if (rst)
            q <= 1'b0;
        else
            q <= d;
    end
endmodule
