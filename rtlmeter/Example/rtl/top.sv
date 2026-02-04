// Synthesizable port of the RTLMeter Example design.
//
// The upstream design is a self-clocking counter that counts to 1,000,000
// and prints every 200,000 cycles.  This version strips all non-synthesizable
// constructs (initial blocks, # delays, $display, $finish, string type,
// DPI-C imports) and exposes proper I/O ports so cocotb can drive clock/reset
// and observe the counter state.
//
// Original: https://github.com/verilator/rtlmeter  designs/Example/src/top.v

module top (
    input  logic        clk,
    input  logic        rst_n,
    output logic [19:0] cnt,
    output logic        milestone,
    output logic        done
);

    // 20-bit counter (enough for 1,000,000)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cnt <= 20'd0;
        end else if (!done) begin
            cnt <= cnt + 20'd1;
        end
    end

    // Milestone flag: asserted when cnt is a multiple of 200,000
    // (mirrors the upstream $display at every 200k cycles)
    always_comb begin
        milestone = (cnt != 20'd0) && (cnt % 20'd200_000 == 20'd0);
    end

    // Done flag: asserted when cnt reaches 1,000,000
    // (mirrors the upstream $finish at 1M cycles)
    always_comb begin
        done = (cnt == 20'd1_000_000);
    end

endmodule
