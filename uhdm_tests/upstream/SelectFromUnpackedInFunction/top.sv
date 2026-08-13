// PATCHED (RyuSim-Validation): upstream source was invalid SV; minimal repair below preserves test intent.
// mixed variable-initializer and continuous assignment; initializer removed
module top(output logic[2:0] o);
   function automatic logic [2:0] get_3rd(logic [2:0] mat [3:0]);
      return mat[3];
   endfunction // get_3rd

   logic [2:0] a [3:0]; // patched: declaration initializer + continuous assign is an illegal mix (LRM 10.3.2)
   assign a[3][2] = 1'b1;

   assign o = get_3rd(a);
endmodule // top
