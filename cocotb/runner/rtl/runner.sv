// Copyright cocotb contributors
// Licensed under the Revised BSD License, see LICENSE for details.
// SPDX-License-Identifier: BSD-3-Clause
//
// Ported for RyuSim: removed `include of basic_hierarchy_module.v,
// initial begin block, `DEFINE/`DEFINE_STR references. The runner
// module is self-contained with parameterized width passthrough.

module runner #(
    parameter WIDTH_IN = 4,
    parameter WIDTH_OUT = 8
) (
    input  [WIDTH_IN-1:0]   data_in,
    output [WIDTH_OUT-1:0]  data_out
);

// Zero-extend data_in to WIDTH_OUT bits
assign data_out = {{(WIDTH_OUT-WIDTH_IN){1'b0}}, data_in};

endmodule
