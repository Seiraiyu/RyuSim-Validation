# BlackParrot — cocotb testbench
#
# BlackParrot is an open-source multicore RISC-V processor from the University
# of Washington. The design consists of three main RTL components:
#   - bp/: BlackParrot core RTL (front-end, back-end, memory engine, CCE)
#   - basejump_stl/: BaseJump STL library (FIFOs, arbiters, memories, NoC)
#   - hardfloat/: Berkeley HardFloat FPU (IEEE 754 recoded format)
#
# Top module: wrapper — wraps bp_processor with a downsampled real-time clock.
# The upstream testbench.sv instantiates wrapper plus nonsynth simulation models
# (clock gen, reset gen, cfg loader, DRAM, host I/O), all replaced by cocotb.
#
# Configuration: 1x1 (single core) for basic compilation and smoke testing.

TOPLEVEL_LANG = verilog
SIM = ryusim

# Source file order follows upstream descriptor.yaml
# Packages must come before modules that use them
VERILOG_SOURCES = \
    rtl/basejump_stl/bsg_axi_pkg.sv \
    rtl/basejump_stl/bsg_cache_pkg.sv \
    rtl/basejump_stl/bsg_noc_pkg.sv \
    rtl/basejump_stl/bsg_wormhole_router_pkg.sv \
    rtl/bp/bp_common_pkg.sv \
    rtl/bp/bp_be_pkg.sv \
    rtl/bp/bp_fe_pkg.sv \
    rtl/bp/bp_me_pkg.sv \
    rtl/bp/bp_top_pkg.sv \
    rtl/basejump_stl/bsg_async_fifo.sv \
    rtl/basejump_stl/bsg_launch_sync_sync.sv \
    rtl/basejump_stl/bsg_sync_sync.sv \
    rtl/basejump_stl/bsg_async_ptr_gray.sv \
    rtl/basejump_stl/bsg_cache.sv \
    rtl/basejump_stl/bsg_cache_dma.sv \
    rtl/basejump_stl/bsg_cache_dma_to_wormhole.sv \
    rtl/basejump_stl/bsg_cache_miss.sv \
    rtl/basejump_stl/bsg_cache_decode.sv \
    rtl/basejump_stl/bsg_cache_sbuf.sv \
    rtl/basejump_stl/bsg_cache_tbuf.sv \
    rtl/basejump_stl/bsg_cache_buffer_queue.sv \
    rtl/basejump_stl/bsg_wormhole_to_cache_dma_fanout.sv \
    rtl/basejump_stl/bsg_channel_tunnel.sv \
    rtl/basejump_stl/bsg_channel_tunnel_in.sv \
    rtl/basejump_stl/bsg_channel_tunnel_out.sv \
    rtl/basejump_stl/bsg_1_to_n_tagged_fifo.sv \
    rtl/basejump_stl/bsg_1_to_n_tagged.sv \
    rtl/basejump_stl/bsg_fifo_1r1w_large.sv \
    rtl/basejump_stl/bsg_fifo_1r1w_pseudo_large.sv \
    rtl/basejump_stl/bsg_fifo_1r1w_small.sv \
    rtl/basejump_stl/bsg_fifo_1r1w_small_unhardened.sv \
    rtl/basejump_stl/bsg_fifo_1rw_large.sv \
    rtl/basejump_stl/bsg_fifo_tracker.sv \
    rtl/basejump_stl/bsg_flow_counter.sv \
    rtl/basejump_stl/bsg_one_fifo.sv \
    rtl/basejump_stl/bsg_parallel_in_serial_out.sv \
    rtl/basejump_stl/bsg_parallel_in_serial_out_dynamic.sv \
    rtl/basejump_stl/bsg_parallel_in_serial_out_passthrough.sv \
    rtl/basejump_stl/bsg_parallel_in_serial_out_passthrough_dynamic.sv \
    rtl/basejump_stl/bsg_serial_in_parallel_out_passthrough_dynamic.sv \
    rtl/basejump_stl/bsg_round_robin_1_to_n.sv \
    rtl/basejump_stl/bsg_round_robin_2_to_2.sv \
    rtl/basejump_stl/bsg_round_robin_n_to_1.sv \
    rtl/basejump_stl/bsg_serial_in_parallel_out.sv \
    rtl/basejump_stl/bsg_serial_in_parallel_out_dynamic.sv \
    rtl/basejump_stl/bsg_serial_in_parallel_out_full.sv \
    rtl/basejump_stl/bsg_serial_in_parallel_out_passthrough.sv \
    rtl/basejump_stl/bsg_shift_reg.sv \
    rtl/basejump_stl/bsg_two_fifo.sv \
    rtl/basejump_stl/bsg_cam_1r1w_replacement.sv \
    rtl/basejump_stl/bsg_cam_1r1w_sync.sv \
    rtl/basejump_stl/bsg_cam_1r1w_tag_array.sv \
    rtl/basejump_stl/bsg_mem_1r1w.sv \
    rtl/basejump_stl/bsg_mem_1r1w_one_hot.sv \
    rtl/basejump_stl/bsg_mem_1r1w_sync_synth.sv \
    rtl/basejump_stl/bsg_mem_1r1w_sync.sv \
    rtl/basejump_stl/bsg_mem_1r1w_synth.sv \
    rtl/basejump_stl/bsg_mem_1rw_sync.sv \
    rtl/basejump_stl/bsg_mem_1rw_sync_mask_write_bit.sv \
    rtl/basejump_stl/bsg_mem_1rw_sync_mask_write_bit_synth.sv \
    rtl/basejump_stl/bsg_mem_1rw_sync_mask_write_byte.sv \
    rtl/basejump_stl/bsg_mem_1rw_sync_mask_write_byte_synth.sv \
    rtl/basejump_stl/bsg_mem_1rw_sync_synth.sv \
    rtl/basejump_stl/bsg_mem_2r1w_sync.sv \
    rtl/basejump_stl/bsg_mem_2r1w_sync_synth.sv \
    rtl/basejump_stl/bsg_mem_3r1w_sync.sv \
    rtl/basejump_stl/bsg_mem_3r1w_sync_synth.sv \
    rtl/basejump_stl/bsg_adder_cin.sv \
    rtl/basejump_stl/bsg_adder_one_hot.sv \
    rtl/basejump_stl/bsg_adder_ripple_carry.sv \
    rtl/basejump_stl/bsg_arb_fixed.sv \
    rtl/basejump_stl/bsg_arb_round_robin.sv \
    rtl/basejump_stl/bsg_array_concentrate_static.sv \
    rtl/basejump_stl/bsg_buf.sv \
    rtl/basejump_stl/bsg_buf_ctrl.sv \
    rtl/basejump_stl/bsg_circular_ptr.sv \
    rtl/basejump_stl/bsg_concentrate_static.sv \
    rtl/basejump_stl/bsg_counting_leading_zeros.sv \
    rtl/basejump_stl/bsg_counter_clear_up.sv \
    rtl/basejump_stl/bsg_counter_clear_up_one_hot.sv \
    rtl/basejump_stl/bsg_counter_clock_downsample.sv \
    rtl/basejump_stl/bsg_counter_set_down.sv \
    rtl/basejump_stl/bsg_counter_set_en.sv \
    rtl/basejump_stl/bsg_counter_up_down.sv \
    rtl/basejump_stl/bsg_counter_up_down_variable.sv \
    rtl/basejump_stl/bsg_crossbar_o_by_i.sv \
    rtl/basejump_stl/bsg_crossbar_control_locking_o_by_i.sv \
    rtl/basejump_stl/bsg_cycle_counter.sv \
    rtl/basejump_stl/bsg_decode.sv \
    rtl/basejump_stl/bsg_decode_with_v.sv \
    rtl/basejump_stl/bsg_dff.sv \
    rtl/basejump_stl/bsg_dff_chain.sv \
    rtl/basejump_stl/bsg_dff_en.sv \
    rtl/basejump_stl/bsg_dff_en_bypass.sv \
    rtl/basejump_stl/bsg_dff_reset.sv \
    rtl/basejump_stl/bsg_dff_reset_en.sv \
    rtl/basejump_stl/bsg_dff_reset_en_bypass.sv \
    rtl/basejump_stl/bsg_dff_reset_set_clear.sv \
    rtl/basejump_stl/bsg_dlatch.sv \
    rtl/basejump_stl/bsg_edge_detect.sv \
    rtl/basejump_stl/bsg_encode_one_hot.sv \
    rtl/basejump_stl/bsg_expand_bitmask.sv \
    rtl/basejump_stl/bsg_gray_to_binary.sv \
    rtl/basejump_stl/bsg_hash_bank.sv \
    rtl/basejump_stl/bsg_hash_bank_reverse.sv \
    rtl/basejump_stl/bsg_imul_iterative.sv \
    rtl/basejump_stl/bsg_idiv_iterative.sv \
    rtl/basejump_stl/bsg_idiv_iterative_controller.sv \
    rtl/basejump_stl/bsg_lfsr.sv \
    rtl/basejump_stl/bsg_lru_pseudo_tree_backup.sv \
    rtl/basejump_stl/bsg_lru_pseudo_tree_decode.sv \
    rtl/basejump_stl/bsg_lru_pseudo_tree_encode.sv \
    rtl/basejump_stl/bsg_locking_arb_fixed.sv \
    rtl/basejump_stl/bsg_mul_add_unsigned.sv \
    rtl/basejump_stl/bsg_mux.sv \
    rtl/basejump_stl/bsg_mux_bitwise.sv \
    rtl/basejump_stl/bsg_mux_butterfly.sv \
    rtl/basejump_stl/bsg_mux_one_hot.sv \
    rtl/basejump_stl/bsg_mux_segmented.sv \
    rtl/basejump_stl/bsg_muxi2_gatestack.sv \
    rtl/basejump_stl/bsg_nor2.sv \
    rtl/basejump_stl/bsg_nor3.sv \
    rtl/basejump_stl/bsg_nand.sv \
    rtl/basejump_stl/bsg_popcount.sv \
    rtl/basejump_stl/bsg_priority_encode.sv \
    rtl/basejump_stl/bsg_priority_encode_one_hot_out.sv \
    rtl/basejump_stl/bsg_reduce.sv \
    rtl/basejump_stl/bsg_reduce_segmented.sv \
    rtl/basejump_stl/bsg_rotate_left.sv \
    rtl/basejump_stl/bsg_rotate_right.sv \
    rtl/basejump_stl/bsg_round_robin_arb.sv \
    rtl/basejump_stl/bsg_scan.sv \
    rtl/basejump_stl/bsg_strobe.sv \
    rtl/basejump_stl/bsg_swap.sv \
    rtl/basejump_stl/bsg_thermometer_count.sv \
    rtl/basejump_stl/bsg_transpose.sv \
    rtl/basejump_stl/bsg_unconcentrate_static.sv \
    rtl/basejump_stl/bsg_xnor.sv \
    rtl/basejump_stl/bsg_mesh_stitch.sv \
    rtl/basejump_stl/bsg_noc_repeater_node.sv \
    rtl/basejump_stl/bsg_wormhole_concentrator.sv \
    rtl/basejump_stl/bsg_wormhole_concentrator_in.sv \
    rtl/basejump_stl/bsg_wormhole_concentrator_out.sv \
    rtl/basejump_stl/bsg_wormhole_router.sv \
    rtl/basejump_stl/bsg_wormhole_router_adapter_in.sv \
    rtl/basejump_stl/bsg_wormhole_router_adapter_out.sv \
    rtl/basejump_stl/bsg_wormhole_router_decoder_dor.sv \
    rtl/basejump_stl/bsg_wormhole_router_input_control.sv \
    rtl/basejump_stl/bsg_wormhole_router_output_control.sv \
    rtl/basejump_stl/bsg_fifo_1r1w_edge.sv \
    rtl/basejump_stl/bsg_fifo_1r1w_rolly.sv \
    rtl/basejump_stl/bsg_bus_pack.sv \
    rtl/basejump_stl/bsg_async_noc_link.sv \
    rtl/basejump_stl/bsg_dff_sync_read.sv \
    rtl/basejump_stl/bsg_rom_param.sv \
    rtl/hardfloat/compareRecFN.v \
    rtl/hardfloat/divSqrtRecFN.v \
    rtl/hardfloat/divSqrtRecFN_medium.v \
    rtl/hardfloat/divSqrtRecFN_small.v \
    rtl/hardfloat/fNToRecFN.v \
    rtl/hardfloat/HardFloat_primitives.v \
    rtl/hardfloat/HardFloat_rawFN.v \
    rtl/hardfloat/iNToRecFN.v \
    rtl/hardfloat/isSigNaNRecFN.v \
    rtl/hardfloat/mulAddRecFN.v \
    rtl/hardfloat/mulRecFN.v \
    rtl/hardfloat/recFNToFN.v \
    rtl/hardfloat/recFNToIN.v \
    rtl/hardfloat/recFNToRecFN.v \
    rtl/hardfloat/HardFloat_specialize.v \
    rtl/bp/bp_mmu.sv \
    rtl/bp/bp_pma.sv \
    rtl/bp/bp_tlb.sv \
    rtl/bp/bp_be_top.sv \
    rtl/bp/bp_be_calculator_top.sv \
    rtl/bp/bp_be_csr.sv \
    rtl/bp/bp_be_fp_box.sv \
    rtl/bp/bp_be_fp_rebox.sv \
    rtl/bp/bp_be_fp_unbox.sv \
    rtl/bp/bp_be_int_unbox.sv \
    rtl/bp/bp_be_int_box.sv \
    rtl/bp/bp_be_pipe_int.sv \
    rtl/bp/bp_be_pipe_aux.sv \
    rtl/bp/bp_be_pipe_fma.sv \
    rtl/bp/bp_be_pipe_long.sv \
    rtl/bp/bp_be_pipe_mem.sv \
    rtl/bp/bp_be_pipe_sys.sv \
    rtl/bp/bp_be_ptw.sv \
    rtl/bp/bp_be_rec_to_raw.sv \
    rtl/bp/bp_be_reservation.sv \
    rtl/bp/bp_be_cmd_queue.sv \
    rtl/bp/bp_be_detector.sv \
    rtl/bp/bp_be_director.sv \
    rtl/bp/bp_be_expander.sv \
    rtl/bp/bp_be_instr_decoder.sv \
    rtl/bp/bp_be_issue_queue.sv \
    rtl/bp/bp_be_regfile.sv \
    rtl/bp/bp_be_scheduler.sv \
    rtl/bp/bp_be_scoreboard.sv \
    rtl/bp/bp_be_dcache.sv \
    rtl/bp/bp_be_dcache_decoder.sv \
    rtl/bp/bp_be_dcache_wbuf.sv \
    rtl/bp/bp_fe_ras.sv \
    rtl/bp/bp_fe_bht.sv \
    rtl/bp/bp_fe_btb.sv \
    rtl/bp/bp_fe_controller.sv \
    rtl/bp/bp_fe_icache.sv \
    rtl/bp/bp_fe_scan.sv \
    rtl/bp/bp_fe_pc_gen.sv \
    rtl/bp/bp_fe_realigner.sv \
    rtl/bp/bp_fe_top.sv \
    rtl/bp/bp_lce.sv \
    rtl/bp/bp_lce_req.sv \
    rtl/bp/bp_lce_cmd.sv \
    rtl/bp/bp_me_bedrock_register.sv \
    rtl/bp/bp_me_cache_controller.sv \
    rtl/bp/bp_me_dram_hash_decode.sv \
    rtl/bp/bp_me_dram_hash_encode.sv \
    rtl/bp/bp_me_cache_slice.sv \
    rtl/bp/bp_me_cfg_slice.sv \
    rtl/bp/bp_me_clint_slice.sv \
    rtl/bp/bp_me_loopback.sv \
    rtl/bp/bp_cce.sv \
    rtl/bp/bp_cce_alu.sv \
    rtl/bp/bp_cce_arbitrate.sv \
    rtl/bp/bp_cce_branch.sv \
    rtl/bp/bp_cce_dir.sv \
    rtl/bp/bp_cce_dir_lru_extract.sv \
    rtl/bp/bp_cce_dir_segment.sv \
    rtl/bp/bp_cce_dir_tag_checker.sv \
    rtl/bp/bp_cce_gad.sv \
    rtl/bp/bp_cce_inst_decode.sv \
    rtl/bp/bp_cce_inst_predecode.sv \
    rtl/bp/bp_cce_inst_ram.sv \
    rtl/bp/bp_cce_inst_stall.sv \
    rtl/bp/bp_cce_msg.sv \
    rtl/bp/bp_cce_pending_bits.sv \
    rtl/bp/bp_cce_pma.sv \
    rtl/bp/bp_cce_reg.sv \
    rtl/bp/bp_cce_spec_bits.sv \
    rtl/bp/bp_cce_src_sel.sv \
    rtl/bp/bp_io_cce.sv \
    rtl/bp/bp_cce_fsm.sv \
    rtl/bp/bp_cce_wrapper.sv \
    rtl/bp/bp_bedrock_size_to_len.sv \
    rtl/bp/bp_uce.sv \
    rtl/bp/bp_me_addr_to_cce_id.sv \
    rtl/bp/bp_me_cce_id_to_cord.sv \
    rtl/bp/bp_me_cord_to_id.sv \
    rtl/bp/bp_me_lce_id_to_cord.sv \
    rtl/bp/bp_me_stream_pump.sv \
    rtl/bp/bp_me_stream_pump_in.sv \
    rtl/bp/bp_me_stream_pump_out.sv \
    rtl/bp/bp_me_stream_pump_control.sv \
    rtl/bp/bp_me_stream_to_wormhole.sv \
    rtl/bp/bp_me_wormhole_header_encode.sv \
    rtl/bp/bp_me_wormhole_to_stream.sv \
    rtl/bp/bp_me_wormhole_stream_control.sv \
    rtl/bp/bp_me_xbar_stream.sv \
    rtl/bp/bp_me_stream_gearbox.sv \
    rtl/bp/bp_nd_socket.sv \
    rtl/bp/bp_cacc_vdp.sv \
    rtl/bp/bp_cacc_tile.sv \
    rtl/bp/bp_cacc_tile_node.sv \
    rtl/bp/bp_cacc_complex.sv \
    rtl/bp/bp_sacc_vdp.sv \
    rtl/bp/bp_sacc_scratchpad.sv \
    rtl/bp/bp_sacc_tile.sv \
    rtl/bp/bp_sacc_tile_node.sv \
    rtl/bp/bp_sacc_complex.sv \
    rtl/bp/bp_core.sv \
    rtl/bp/bp_core_lite.sv \
    rtl/bp/bp_core_minimal.sv \
    rtl/bp/bp_core_complex.sv \
    rtl/bp/bp_l2e_tile.sv \
    rtl/bp/bp_l2e_tile_node.sv \
    rtl/bp/bp_io_complex.sv \
    rtl/bp/bp_io_link_to_lce.sv \
    rtl/bp/bp_io_tile.sv \
    rtl/bp/bp_io_tile_node.sv \
    rtl/bp/bp_mem_complex.sv \
    rtl/bp/bp_multicore.sv \
    rtl/bp/bp_unicore.sv \
    rtl/bp/bp_unicore_lite.sv \
    rtl/bp/bp_core_tile.sv \
    rtl/bp/bp_core_tile_node.sv \
    rtl/bp/bp_processor.sv \
    rtl/bp/wrapper.sv \
    rtl/basejump_stl/bsg_tag_pkg.sv \
    rtl/basejump_stl/bsg_cache_to_axi.sv \
    rtl/basejump_stl/bsg_cache_to_axi_rx.sv \
    rtl/basejump_stl/bsg_cache_to_axi_tx.sv \
    rtl/basejump_stl/bsg_cache_to_axi_ordering.sv \
    rtl/basejump_stl/bsg_cache_to_test_dram.sv \
    rtl/basejump_stl/bsg_cache_to_test_dram_rx.sv \
    rtl/basejump_stl/bsg_cache_to_test_dram_rx_reorder.sv \
    rtl/basejump_stl/bsg_cache_to_test_dram_tx.sv \
    rtl/basejump_stl/bsg_fifo_reorder.sv \
    rtl/basejump_stl/bsg_flatten_2D_array.sv \
    rtl/basejump_stl/bsg_make_2D_array.sv \
    rtl/basejump_stl/bsg_cam_1r1w_unmanaged.sv \
    rtl/basejump_stl/bsg_mux2_gatestack.sv \
    rtl/basejump_stl/bsg_tag_master.sv \
    rtl/basejump_stl/bsg_tag_client.sv \
    rtl/basejump_stl/bsg_tag_client_unsync.sv

# Include paths for header files
VERILOG_INCLUDE_DIRS = rtl/basejump_stl rtl/bp rtl/hardfloat

# Compile-time defines (1x1 single-core configuration)
EXTRA_ARGS += \
    -Dden2048Mb=1 \
    -Dsg5=1 \
    -Dx16=1 \
    -DFULL_MEM=1 \
    -DBP_CFG_FLOWVAR=e_bp_multicore_1_cfg \
    -DBSG_HIDE_FROM_SYNTHESIS=1

# Limit VPI depth to top-level ports (faster compile on CI)
EXTRA_ARGS += --vpi-depth 1

# Parallelize C++ compilation of generated simulation code
EXTRA_ARGS += --jobs 4

TOPLEVEL = wrapper
MODULE = test_blackparrot

export PYTHONPATH := $(CURDIR)/cocotb

include $(shell cocotb-config --makefiles)/Makefile.sim
