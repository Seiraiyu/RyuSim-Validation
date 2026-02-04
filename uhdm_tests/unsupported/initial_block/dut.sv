module bad_initial (
    output logic [7:0] o
);
    initial begin
        o = 8'hFF;
    end
endmodule
