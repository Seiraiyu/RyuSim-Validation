module bad_fork (
    input logic clk,
    output logic [7:0] o
);
    initial begin
        fork
            o = 8'h01;
        join
    end
endmodule
