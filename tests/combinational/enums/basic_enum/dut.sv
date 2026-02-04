// IEEE 1800-2023 Section 6.19 - Enumerations
module basic_enum (
    input  logic [1:0] sel,
    output logic [7:0] out
);
    typedef enum logic [1:0] {
        IDLE  = 2'b00,
        RUN   = 2'b01,
        DONE  = 2'b10,
        ERROR = 2'b11
    } state_t;

    state_t state;
    assign state = state_t'(sel);
    assign out = (state == IDLE)  ? 8'd0 :
                 (state == RUN)   ? 8'd1 :
                 (state == DONE)  ? 8'd2 : 8'd255;
endmodule
