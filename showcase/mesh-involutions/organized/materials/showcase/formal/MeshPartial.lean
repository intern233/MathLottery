import MeshDefinitions
import MeshStructure
import MeshSymmetry
import MeshComponents
import MeshRotation
import MeshEquivariance
import MeshNesting
import MeshCompatibility
import MeshOrbitCounting
import MeshPolynomial
import MeshTransport
import MeshReduction

/-! All imports are checked partial results. No unconditional conjecture proof. -/

#check Mesh.correctedConjecture
#check @Mesh.correctedConjecture_of_markedTransport

#print axioms Mesh.band_literal
#print axioms Mesh.empty_R_expansion
#print axioms Mesh.forbidden_iff_geom
#print axioms Mesh.mesh_A
#print axioms Mesh.mesh_B
#print axioms Mesh.A_unique_out
#print axioms Mesh.A_no_chain
#print axioms Mesh.A_leaves_decrease
#print axioms Mesh.B_unique_in
#print axioms Mesh.B_unique_out
#print axioms Mesh.A_noncrossing
#print axioms Mesh.B_noncrossing
#print axioms Mesh.geom_transpose
#print axioms Mesh.A_inverse
#print axioms Mesh.B_inverse
#print axioms Mesh.transpose_twice
#print axioms Mesh.rc_apply
#print axioms Mesh.rc_rc
#print axioms Mesh.rc_preserves_involutive
#print axioms Mesh.rc_involutive_iff
#print axioms Mesh.band_reverse
#print axioms Mesh.min_rev
#print axioms Mesh.max_rev
#print axioms Mesh.R_reverse
#print axioms Mesh.R_coords
#print axioms Mesh.empty_reverse
#print axioms Mesh.mesh_reverse
#print axioms Mesh.reverseEdge_apply
#print axioms Mesh.occurrences_reverse_card
#print axioms Mesh.distribution_reverse
#print axioms Mesh.IncTo.mono
#print axioms Mesh.IncTo.reflect
#print axioms Mesh.chain_cases
#print axioms Mesh.DecTo.lt
#print axioms Mesh.DecTo.le
#print axioms Mesh.star_outside
#print axioms Mesh.path_outside
#print axioms Mesh.outside_left
#print axioms Mesh.outside_gap_upper
#print axioms Mesh.outside_star_middle
#print axioms Mesh.outside_star
#print axioms Mesh.outside_path_right
#print axioms Mesh.outside_path
#print axioms Mesh.star_characterization
#print axioms Mesh.path_characterization
#print axioms Mesh.positionShift_next
#print axioms Mesh.positionShift_last
#print axioms Mesh.positionShift_fixed
#print axioms Mesh.rotateForward_first
#print axioms Mesh.rotateForward_next
#print axioms Mesh.rotateBackward_next
#print axioms Mesh.rotateBackward_last
#print axioms Mesh.rotateForward_fixed
#print axioms Mesh.rotateBackward_fixed
#print axioms Mesh.rotate_backward_forward
#print axioms Mesh.rotate_forward_backward
#print axioms Mesh.outside_transfer
#print axioms Mesh.rotateForward_layout
#print axioms Mesh.rotateBackward_layout
#print axioms Mesh.single_star_to_path
#print axioms Mesh.single_path_to_star
#print axioms Mesh.inversePositions_inc
#print axioms Mesh.inverseValues_dec
#print axioms Mesh.inverse_star_layout
#print axioms Mesh.inverse_rotation
#print axioms Mesh.transpose_star_edge
#print axioms Mesh.transpose_path_edge
#print axioms Mesh.star_edge_index_under_inverse
#print axioms Mesh.individual_edge_equivariance
#print axioms Mesh.star_gap_nesting
#print axioms Mesh.path_gap_nesting
#print axioms Mesh.outside_exterior_transfer
#print axioms Mesh.outer_value_options
#print axioms Mesh.rotateForward_preserves_inner
#print axioms Mesh.rotateBackward_preserves_inner
#print axioms Mesh.star_values_covered
#print axioms Mesh.path_values_covered
#print axioms Mesh.nested_value_bounds
#print axioms Mesh.OrbitCounting.self_mem_orbit
#print axioms Mesh.OrbitCounting.orbit_eq_of_mem
#print axioms Mesh.OrbitCounting.union_all_orbits
#print axioms Mesh.OrbitCounting.orbits_mono
#print axioms Mesh.OrbitCounting.union_sub_orbits
#print axioms Mesh.OrbitCounting.union_sub_stable
#print axioms Mesh.OrbitCounting.orbits_union_sub
#print axioms Mesh.OrbitCounting.distinct_orbits_disjoint
#print axioms Mesh.OrbitCounting.sum_orbit_cards
#print axioms Mesh.OrbitCounting.invariant_subsets_sum
#print axioms Mesh.OrbitCounting.weighted_invariant_subset_expansion
#print axioms Mesh.OrbitCounting.orbit_size_one_or_two
#print axioms Mesh.distribution_as_filter
#print axioms Mesh.generating_coeff
#print axioms Mesh.generating_eq_iff_distributions
#print axioms Mesh.involutive_symm
#print axioms Mesh.occurrence_transpose_stable
#print axioms Mesh.occurrence_transpose_involutive
#print axioms Mesh.actual_orbit_expansion
#print axioms Mesh.actual_generating_marked_expansion
#print axioms Mesh.OrbitCounting.member_orbit_subset
#print axioms Mesh.OrbitCounting.orbit_image
#print axioms Mesh.OrbitCounting.orbits_transport
#print axioms Mesh.OrbitCounting.orbit_weight_transport
#print axioms Mesh.fixedMarked_info
#print axioms Mesh.generating_as_fixedMarked
#print axioms Mesh.MarkedTransport.preserves_weight
#print axioms Mesh.generating_eq_of_markedTransport
#print axioms Mesh.correctedConjecture_of_markedTransport
