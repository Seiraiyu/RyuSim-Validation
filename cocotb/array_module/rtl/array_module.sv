// Copyright cocotb contributors
// Copyright (c) 2016 Potential Ventures Ltd
// Copyright (c) 2016 SolarFlare Communications Inc
// Licensed under the Revised BSD License, see LICENSE for details.
// SPDX-License-Identifier: BSD-3-Clause
//
// Ported for RyuSim: stripped timescale directive.

typedef struct {
    logic a;
    logic [7:0] b[0:2];
} rec_type;

module array_module (
    input                                       clk,

    input  integer                              select_in,

    input          [7:0]                        port_desc_in,
    input          [0:7]                        port_asc_in,
    input          [1:8]                        port_ofst_in,

    output         [7:0]                        port_desc_out,
    output         [0:7]                        port_asc_out,
    output         [1:8]                        port_ofst_out,

    output logic                                port_logic_out,
    output logic   [7:0]                        port_logic_vec_out,
    output rec_type                             port_rec_out,
    output rec_type                             port_cmplx_out[0:1]
);

parameter logic          param_logic       = 1'b1;
parameter logic [7:0]    param_logic_vec   = 8'hDA;

localparam logic          const_logic       = 1'b0;
localparam logic [7:0]    const_logic_vec   = 8'h3D;

wire [0:3]       sig_t1;
wire [7:0]       sig_t2[7:4];
wire [7:0]       sig_t3a[1:4];
wire [7:0]       sig_t3b[3:0];
wire [7:0]       sig_t4[0:3][7:4];
wire [7:0]       sig_t5[0:2][0:3];
wire [7:0]       sig_t6[0:1][2:4];

wire       [16:23]  sig_asc;
wire       [23:16]  sig_desc;
wire logic          sig_logic;
wire logic [7:0]    sig_logic_vec;
     rec_type       sig_rec;
     rec_type       sig_cmplx [0:1];

typedef logic [7:0] uint16_t;

uint16_t sig_t7 [3:0][3:0];
uint16_t [3:0][3:0] sig_t8;

assign port_ofst_out = port_ofst_in;

always @(posedge clk) begin
    if (select_in == 1) begin
        port_logic_out         = const_logic;
        port_logic_vec_out     = const_logic_vec;
        port_rec_out.a         = sig_rec.a;
        port_rec_out.b[0]      = sig_rec.b[0];
        port_rec_out.b[1]      = sig_rec.b[1];
        port_rec_out.b[2]      = sig_rec.b[2];
        port_cmplx_out[0].a    = sig_cmplx[0].a;
        port_cmplx_out[0].b[0] = sig_cmplx[0].b[0];
        port_cmplx_out[0].b[1] = sig_cmplx[0].b[1];
        port_cmplx_out[0].b[2] = sig_cmplx[0].b[2];
        port_cmplx_out[1].a    = sig_cmplx[1].a;
        port_cmplx_out[1].b[0] = sig_cmplx[1].b[0];
        port_cmplx_out[1].b[1] = sig_cmplx[1].b[1];
        port_cmplx_out[1].b[2] = sig_cmplx[1].b[2];
    end else begin
        if (select_in == 2) begin
            port_logic_out         = sig_logic;
            port_logic_vec_out     = sig_logic_vec;
            port_rec_out.a         = sig_rec.a;
            port_rec_out.b[0]      = sig_rec.b[0];
            port_rec_out.b[1]      = sig_rec.b[1];
            port_rec_out.b[2]      = sig_rec.b[2];
            port_cmplx_out[0].a    = sig_cmplx[0].a;
            port_cmplx_out[0].b[0] = sig_cmplx[0].b[0];
            port_cmplx_out[0].b[1] = sig_cmplx[0].b[1];
            port_cmplx_out[0].b[2] = sig_cmplx[0].b[2];
            port_cmplx_out[1].a    = sig_cmplx[1].a;
            port_cmplx_out[1].b[0] = sig_cmplx[1].b[0];
            port_cmplx_out[1].b[1] = sig_cmplx[1].b[1];
            port_cmplx_out[1].b[2] = sig_cmplx[1].b[2];
        end else begin
            port_logic_out         = param_logic;
            port_logic_vec_out     = param_logic_vec;
            port_rec_out.a         = sig_rec.a;
            port_rec_out.b[0]      = sig_rec.b[0];
            port_rec_out.b[1]      = sig_rec.b[1];
            port_rec_out.b[2]      = sig_rec.b[2];
            port_cmplx_out[0].a    = sig_cmplx[0].a;
            port_cmplx_out[0].b[0] = sig_cmplx[0].b[0];
            port_cmplx_out[0].b[1] = sig_cmplx[0].b[1];
            port_cmplx_out[0].b[2] = sig_cmplx[0].b[2];
            port_cmplx_out[1].a    = sig_cmplx[1].a;
            port_cmplx_out[1].b[0] = sig_cmplx[1].b[0];
            port_cmplx_out[1].b[1] = sig_cmplx[1].b[1];
            port_cmplx_out[1].b[2] = sig_cmplx[1].b[2];
        end
    end
end

genvar idx1;
generate
for (idx1 = 16; idx1 <= 23; idx1=idx1+1) begin:asc_gen
    localparam OFFSET = 16-0;
    reg sig;
    always @(posedge clk) begin
        sig <= port_asc_in[idx1-OFFSET];
    end
    assign sig_asc[idx1] = sig;
    assign port_asc_out[idx1-OFFSET] = sig_asc[idx1];
end
endgenerate

genvar idx2;
generate
for (idx2 = 7; idx2 >= 0; idx2=idx2-1) begin:desc_gen
    localparam OFFSET = 23-7;
    reg sig;
    always @(posedge clk) begin
        sig <= port_desc_in[idx2];
    end
    assign sig_desc[idx2+OFFSET] = sig;
    assign port_desc_out[idx2] = sig_desc[idx2+OFFSET];
end
endgenerate

endmodule
