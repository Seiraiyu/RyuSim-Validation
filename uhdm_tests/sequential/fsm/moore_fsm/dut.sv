// IEEE 1800-2023 Section 9.4.2 - Moore FSM with always_ff and always_comb
module moore_fsm (
    input  logic clk,
    input  logic rst,
    input  logic in_bit,
    output logic [1:0] state_out
);
    typedef enum logic [1:0] {
        S0 = 2'b00,
        S1 = 2'b01,
        S2 = 2'b10
    } state_t;

    state_t state, next_state;

    always_ff @(posedge clk) begin
        if (rst)
            state <= S0;
        else
            state <= next_state;
    end

    always_comb begin
        case (state)
            S0: next_state = in_bit ? S1 : S0;
            S1: next_state = in_bit ? S2 : S0;
            S2: next_state = S0;
            default: next_state = S0;
        endcase
    end

    assign state_out = state;
endmodule
