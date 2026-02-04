// Copyright cocotb contributors
// Copyright (c) 2013, 2018 Potential Ventures Ltd
// Copyright (c) 2013 SolarFlare Communications Inc
// Licensed under the Revised BSD License, see LICENSE for details.
// SPDX-License-Identifier: BSD-3-Clause
//
// Ported for RyuSim: stripped timescale, initial blocks, $display,
// __ICARUS__ ifdefs, _VCP ifdefs, string/real/integer types, and
// extended identifiers.

typedef struct packed
{
    logic val_a;
    logic val_b;
    logic value;
} test_struct_packed;

module sub;
   reg subsig1;
   reg subsig2;
   wire redundant = subsig1 | subsig2;
endmodule : sub

module sample_module #(
    parameter INT_PARAM = 12
)(
    input                                       clk,

    output reg                                  stream_in_ready,
    input                                       stream_in_valid,
    input  test_struct_packed                   my_struct,
    input  [7:0]                                stream_in_data,
    input  [31:0]                               stream_in_data_dword,
    input  [38:0]                               stream_in_data_39bit,
    input  [63:0]                               stream_in_data_wide,
    input  [127:0]                              stream_in_data_dqword,

    input                                       stream_out_ready,
    output reg [7:0]                            stream_out_data_comb,
    output reg [7:0]                            stream_out_data_registered,

    output                                      and_output

);

always @(posedge clk)
    stream_out_data_registered <= stream_in_data;

always @(stream_in_data)
    stream_out_data_comb = stream_in_data;

always @(stream_out_ready)
    stream_in_ready      = stream_out_ready;

and test_and_gate(and_output, stream_in_ready, stream_in_valid);

parameter NUM_OF_MODULES = 4;
reg[NUM_OF_MODULES-1:0] temp;
genvar idx;
generate
    for (idx = 0; idx < NUM_OF_MODULES; idx=idx+1) begin
        always @(posedge clk) begin
            temp[idx] <= 1'b0;
        end
    end
endgenerate

generate
    if (INT_PARAM == 12) begin : cond_scope
        localparam int scoped_param = 1;
        sub scoped_sub ();
    end else begin : cond_scope_else
        sub scoped_sub_else ();
    end
endgenerate

genvar i;
generate
    for (i = 1; i <= 2; i = i + 1) begin : arr
        sub arr_sub();
    end

    for (i = 1; i <= 2; i = i + 1) begin : outer_scope
        localparam int outer_param = i * 2;
        genvar j;
        for (j = 1; j <= 2; j = j + 1) begin : inner_scope
            localparam int inner_param = outer_param + 1;
            sub inner_sub();
        end
    end
endgenerate

reg [7:0] register_array [1:0];
always @(posedge clk) begin
    register_array[0] <= 0;
end

reg [7:0]  array_7_downto_4[7:4];
reg [7:0]  array_4_to_7[4:7];
reg [7:0]  array_4_downto_7[4:7];
reg [7:0]  array_3_downto_0[3:0];
reg [7:0]  array_0_to_3[0:3];
reg [7:0]  array_2d[0:1][31:28];
always @(posedge stream_in_valid) begin
    array_7_downto_4[4] <= 0;
    array_4_to_7[7] <= 0;
    array_4_downto_7[7] <= 0;
    array_3_downto_0[0] <= 0;
    array_0_to_3[3] <= 0;
    array_2d[1][28] <= 0;
end

logic logic_a, logic_b, logic_c;
assign logic_a = stream_in_valid;
always@* logic_b = stream_in_valid;
always@(posedge clk) logic_c <= stream_in_valid;

bit mybit;
bit [1:0] mybits;
bit [1:0] mybits_uninitialized;

endmodule
