from parapy.core import *
from parapy.geom import *
from parapy.exchange.step import STEPWriter
from classes.wing_primitives.external.wing import Wing
from classes.fuselage_primitives.fuselage import Fuselage
from classes.analysis.scissor_plot import ScissorPlot
import kbeutils.avl as avl
import os
import math
import numpy as np
from scipy import interpolate


class Aircraft(GeomBase):
    """ This is the class representing the overall aircraft.
    """
    # Aircraft weights
    ZFM = Input(validator=val.is_positive)
    fuel_fraction = Input(validator=val.Range(0, 1))

    # Cruise inputs
    velocity = Input(validator=val.is_positive)
    mach = Input(validator=val.is_positive)
    reynolds = Input(validator=val.is_positive)
    air_density = Input(validator=val.is_positive)
    ult_load_factor = Input(validator=val.is_positive)
    g0 = Input(validator=val.is_positive)

    # Stability inputs
    stability_margin = Input(validator=val.is_positive)

    # Fuselage Inputs
    fuselage_tail_angle = Input()
    fuselage_tail_length = Input()
    fuselage_cockpit_length = Input()
    fuselage_cabin_length = Input()
    fuselage_diameter = Input()
    fuselage_nose_length = Input()

    # Tail configuration inputs
    tail_type = Input('conventional', validator=val.OneOf(['conventional',
                                                           't-tail']))
    # Main wing Inputs --------------------------------------------------------
    main_wing_long_pos = Input(validator=val.Range(0, 1))
    main_wing_trans_pos = Input(validator=val.Range(0, 1))
    main_wing_lat_pos = Input(validator=val.Range(0, 1))

    mw_n_wing_segments = Input(validator=lambda x: isinstance(x, int))

    mw_airfoil_names = Input()
    mw_chords = Input(validator=val.all_is_number)
    mw_twists = Input(validator=val.all_is_number)

    mw_sweeps_le = Input(validator=val.all_is_number)
    mw_dihedral_angles = Input(validator=val.all_is_number)

    mw_spanwise_positions = Input(
        validator=lambda lst: all(0 < x < 1 or x is None for x in lst)
    )

    mw_span = Input(validator=val.is_positive)
    mw_wing_cant = Input(validator=val.is_number)

    # Spar inputs
    mw_n_spars = Input(validator=lambda x: isinstance(x, int))
    mw_spar_chordwise_positions = Input(
        validator=lambda lst: all(isinstance(sublist, list)
                                  for sublist in lst)
    )
    mw_spar_aspect_ratios = Input(validator=val.all_is_number)
    mw_spar_profiles = Input(validator=val.all_is_string)
    mw_spar_spanwise_positions_end = Input(validator=val.all_is_number)

    # Rib inputs
    mw_n_ribs_wb = Input(validator=lambda x: isinstance(x, int))
    mw_ribs_wb_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    mw_ribs_wb_spanwise_positions = Input(validator=val.all_is_number)
    mw_ribs_wb_orientation_reference_spars = Input(validator=val.all_is_number)
    mw_ribs_wb_orientation_angles = Input()

    mw_n_ribs_te = Input(validator=lambda x: isinstance(x, int))
    mw_ribs_te_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    mw_ribs_te_spanwise_positions = Input(validator=val.all_is_number)
    mw_ribs_te_orientation_reference_spars = Input(validator=val.all_is_number)
    mw_ribs_te_orientation_angles = Input()

    mw_n_ribs_le = Input(validator=lambda x: isinstance(x, int))
    mw_ribs_le_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    mw_ribs_le_spanwise_positions = Input(validator=val.all_is_number)
    mw_ribs_le_orientation_reference_spars = Input(validator=val.all_is_number)
    mw_ribs_le_orientation_angles = Input()

    # Fuel tank input
    mw_fuel_tank_boundaries = Input(validator=val.all_is_number)

    # Movable input
    mw_n_movables = Input(validator=lambda x: isinstance(x, int))
    mw_movable_spanwise_starts = Input(validator=val.all_is_number)
    mw_movable_spanwise_ends = Input(validator=val.all_is_number)
    mw_movable_hingeline_starts = Input(validator=val.all_is_number)
    mw_movable_deflections = Input(validator=val.all_is_number)
    mw_movables_symmetric = Input(validator=val.all_is_number)
    mw_movables_names = Input(validator=val.all_is_string)

    # Engines input
    mw_n_engines = Input(validator=lambda x: isinstance(x, int) and x % 2 == 0)
    mw_engine_spanwise_positions = Input(validator=val.all_is_number)
    mw_engine_overhangs = Input(validator=val.all_is_number)
    mw_engine_thrusts = Input(validator=val.all_is_number)
    mw_engine_specific_fuel_consumptions = Input(validator=val.all_is_number)
    mw_engine_diameters_inlet = Input([2., 2.], validator=val.all_is_number)
    mw_engine_diameters_outlet = Input([1., 1.], validator=val.all_is_number)
    mw_engine_diameters_part2 = Input([.5, .5], validator=val.all_is_number)
    mw_engine_length_cones1 = Input([2., 2.], validator=val.all_is_number)
    mw_engine_length_cones2 = Input([1., 1.], validator=val.all_is_number)

    @Input
    def mw_semi_span(self):
        return self.mw_span / 2.

    # Horizontal tail Inputs --------------------------------------------------
    horizontal_tail_trans_pos = Input(validator=val.Range(0, 1))
    horizontal_tail_lat_pos = Input(validator=val.Range(0, 1))

    ht_n_wing_segments = Input(validator=lambda x: isinstance(x, int))

    ht_airfoil_names = Input()
    ht_chords = Input(validator=val.all_is_number)
    ht_twists = Input(validator=val.all_is_number)

    ht_sweeps_le = Input(validator=val.all_is_number)
    ht_dihedral_angles = Input(validator=val.all_is_number)

    ht_spanwise_positions = Input(
        validator=lambda lst: all(0 < x < 1 or x is None for x in lst)
    )

    ht_span = Input(validator=val.is_positive)
    ht_wing_cant = Input(validator=val.is_number)

    # Spar inputs
    ht_n_spars = Input(validator=lambda x: isinstance(x, int))
    ht_spar_chordwise_positions = Input(
        validator=lambda lst: all(isinstance(sublist, list)
                                  for sublist in lst)
    )
    ht_spar_aspect_ratios = Input(validator=val.all_is_number)
    ht_spar_profiles = Input(validator=val.all_is_string)
    ht_spar_spanwise_positions_end = Input(validator=val.all_is_number)

    # Rib inputs
    ht_n_ribs_wb = Input(validator=lambda x: isinstance(x, int))
    ht_ribs_wb_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    ht_ribs_wb_spanwise_positions = Input(validator=val.all_is_number)
    ht_ribs_wb_orientation_reference_spars = Input(validator=val.all_is_number)
    ht_ribs_wb_orientation_angles = Input()

    ht_n_ribs_te = Input(validator=lambda x: isinstance(x, int))
    ht_ribs_te_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    ht_ribs_te_spanwise_positions = Input(validator=val.all_is_number)
    ht_ribs_te_orientation_reference_spars = Input(validator=val.all_is_number)
    ht_ribs_te_orientation_angles = Input()

    ht_n_ribs_le = Input(validator=lambda x: isinstance(x, int))
    ht_ribs_le_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    ht_ribs_le_spanwise_positions = Input(validator=val.all_is_number)
    ht_ribs_le_orientation_reference_spars = Input(validator=val.all_is_number)
    ht_ribs_le_orientation_angles = Input()

    # Fuel tank input
    ht_fuel_tank_boundaries = Input(validator=val.all_is_number)

    # Movable input
    ht_n_movables = Input(validator=lambda x: isinstance(x, int))
    ht_movable_spanwise_starts = Input(validator=val.all_is_number)
    ht_movable_spanwise_ends = Input(validator=val.all_is_number)
    ht_movable_hingeline_starts = Input(validator=val.all_is_number)
    ht_movable_deflections = Input(validator=val.all_is_number)
    ht_movables_symmetric = Input(validator=val.all_is_number)
    ht_movables_names = Input(validator=val.all_is_string)

    # Engines input
    ht_n_engines = Input(0, validator=lambda x: isinstance(x, int))
    ht_engine_spanwise_positions = Input(validator=val.all_is_number)
    ht_engine_overhangs = Input(validator=val.all_is_number)
    ht_engine_thrusts = Input(validator=val.all_is_number)
    ht_engine_specific_fuel_consumptions = Input(validator=val.all_is_number)
    ht_engine_diameters_inlet = Input([2., 2.], validator=val.all_is_number)
    ht_engine_diameters_outlet = Input([1., 1.], validator=val.all_is_number)
    ht_engine_diameters_part2 = Input([.5, .5], validator=val.all_is_number)
    ht_engine_length_cones1 = Input([2., 2.], validator=val.all_is_number)
    ht_engine_length_cones2 = Input([1., 1.], validator=val.all_is_number)

    @Input
    def ht_semi_span(self):
        return self.ht_span / 2.

    # Vertical tail Inputs --------------------------------------------------
    vertical_tail_trans_pos = Input(validator=val.Range(0, 1))

    vt_n_wing_segments = Input(validator=lambda x: isinstance(x, int))

    vt_airfoil_names = Input()
    vt_chords = Input(validator=val.all_is_number)
    vt_twists = Input(validator=val.all_is_number)

    vt_sweeps_le = Input(validator=val.all_is_number)
    vt_dihedral_angles = Input(validator=val.all_is_number)

    vt_spanwise_positions = Input(
        validator=lambda lst: all(0 < x < 1 or x is None for x in lst)
    )

    vt_semi_span = Input(validator=val.is_positive)
    vt_wing_cant = Input(validator=val.is_number)

    # Spar inputs
    vt_n_spars = Input(validator=lambda x: isinstance(x, int))
    vt_spar_chordwise_positions = Input(
        validator=lambda lst: all(isinstance(sublist, list)
                                  for sublist in lst)
    )
    vt_spar_aspect_ratios = Input(validator=val.all_is_number)
    vt_spar_profiles = Input(validator=val.all_is_string)
    vt_spar_spanwise_positions_end = Input(validator=val.all_is_number)

    # Rib inputs
    vt_n_ribs_wb = Input(validator=lambda x: isinstance(x, int))
    vt_ribs_wb_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    vt_ribs_wb_spanwise_positions = Input(validator=val.all_is_number)
    vt_ribs_wb_orientation_reference_spars = Input(validator=val.all_is_number)
    vt_ribs_wb_orientation_angles = Input()

    vt_n_ribs_te = Input(validator=lambda x: isinstance(x, int))
    vt_ribs_te_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    vt_ribs_te_spanwise_positions = Input(validator=val.all_is_number)
    vt_ribs_te_orientation_reference_spars = Input(validator=val.all_is_number)
    vt_ribs_te_orientation_angles = Input()

    vt_n_ribs_le = Input(validator=lambda x: isinstance(x, int))
    vt_ribs_le_spanwise_reference_spars_idx = Input(
        validator=val.all_is_number)
    vt_ribs_le_spanwise_positions = Input(validator=val.all_is_number)
    vt_ribs_le_orientation_reference_spars = Input(validator=val.all_is_number)
    vt_ribs_le_orientation_angles = Input()

    # Fuel tank input
    vt_fuel_tank_boundaries = Input(validator=val.all_is_number)

    # Movable input
    vt_n_movables = Input(validator=lambda x: isinstance(x, int))
    vt_movable_spanwise_starts = Input(validator=val.all_is_number)
    vt_movable_spanwise_ends = Input(validator=val.all_is_number)
    vt_movable_hingeline_starts = Input(validator=val.all_is_number)
    vt_movable_deflections = Input(validator=val.all_is_number)
    vt_movables_symmetric = Input(validator=val.all_is_number)
    vt_movables_names = Input(validator=val.all_is_string)

    # Engines input
    vt_n_engines = Input(0, validator=lambda x: isinstance(x, int))
    vt_engine_spanwise_positions = Input(validator=val.all_is_number)
    t_engine_overhangs = Input(validator=val.all_is_number)
    vt_engine_thrusts = Input(validator=val.all_is_number)
    vt_engine_specific_fuel_consumptions = Input(validator=val.all_is_number)
    vt_engine_diameters_inlet = Input([2., 2.], validator=val.all_is_number)
    vt_engine_diameters_outlet = Input([1., 1.], validator=val.all_is_number)
    vt_engine_diameters_part2 = Input([.5, .5], validator=val.all_is_number)
    vt_engine_length_cones1 = Input([2., 2.], validator=val.all_is_number)
    vt_engine_length_cones2 = Input([1., 1.], validator=val.all_is_number)

    __initargs__ = [
        # Aircraft weights
        'ZFM', 'fuel_fraction',
        # Cruise parameters
        'velocity', 'mach', 'reynolds', 'air_density', 'ult_load_factor', 'g0',
        # Fuselage inputs -----------------------------------------------------
        'fuselage_diameter', 'fuselage_tail_angle', 'fuselage_tail_length',
        'fuselage_cockpit_length', 'fuselage_cabin_length',
        'fuselage_nose_length'
        # Tail configuration inputs
        'tail_type',
        # Main wing inputs ----------------------------------------------------
        # Positioning
        'main_wing_long_pos', 'main_wing_trans_pos', 'main_wing_lat_pos',
        # Main wing segments inputs
        'mw_n_wing_segments', 'mw_airfoil_names', 'mw_chords', 'mw_twists',
        'mw_sweeps_le', 'mw_dihedral_angles', 'mw_spanwise_positions',
        'mw_semi_span', 'mw_wing_cant',
        # Main wing spars inputs
        'mw_n_spars',
        'mw_spar_chordwise_positions', 'mw_spar_aspect_ratios',
        'mw_spar_profiles', 'mw_spar_spanwise_positions_end',
        # Main wing wing box ribs inputs
        'mw_n_ribs_wb',
        'mw_ribs_wb_spanwise_reference_spars_idx',
        'mw_ribs_wb_spanwise_positions',
        'mw_ribs_wb_orientation_reference_spars',
        'mw_ribs_wb_orientation_angles',
        # Main wing trailing edge riblets inputs
        'mw_n_ribs_te',
        'mw_ribs_te_spanwise_reference_spars_idx',
        'mw_ribs_te_spanwise_positions',
        'mw_ribs_te_orientation_reference_spars',
        'mw_ribs_te_orientation_angles',
        # Main wing leading edge riblets inputs
        'mw_n_ribs_le',
        'mw_ribs_le_spanwise_reference_spars_idx',
        'mw_ribs_le_spanwise_positions',
        'mw_ribs_le_orientation_reference_spars',
        'mw_ribs_le_orientation_angles',
        # Fuel tanks inputs
        'mw_fuel_tank_boundaries',
        # Main wing movables inputs
        'mw_n_movables',
        'mw_movable_spanwise_starts', 'mw_movable_spanwise_ends',
        'mw_movable_hingeline_starts', 'mw_movable_deflections',
        'mw_movables_symmetric',
        # Main wing engines inputs
        'mw_n_engines',
        'mw_engine_spanwise_positions', 'mw_engine_overhangs',
        'mw_engine_thrusts',
        'mw_engine_specific_fuel_consumptions',
        # Horizontal tail inputs ----------------------------------------------
        # Positioning
        'horizontal_tail_trans_pos', 'horizontal_tail_lat_pos',
        # Horizontal tail wing segments inputs
        'ht_n_wing_segments',
        'ht_airfoil_names', 'ht_chords', 'ht_twists',
        'ht_sweeps_le', 'ht_dihedral_angles', 'ht_spanwise_positions',
        'ht_semi_span', 'ht_wing_cant',
        # Horizontal tail spars inputs
        'ht_n_spars',
        'ht_spar_chordwise_positions', 'ht_spar_aspect_ratios',
        'ht_spar_profiles', 'ht_spar_spanwise_positions_end',
        # Horizontal tail box ribs inputs
        'ht_n_ribs_wb',
        'ht_ribs_wb_spanwise_reference_spars_idx',
        'ht_ribs_wb_spanwise_positions',
        'ht_ribs_wb_orientation_reference_spars',
        'ht_ribs_wb_orientation_angles',
        # Horizontal tail trailing edge riblets inputs
        'ht_n_ribs_te',
        'ht_ribs_te_spanwise_reference_spars_idx',
        'ht_ribs_te_spanwise_positions',
        'ht_ribs_te_orientation_reference_spars',
        'ht_ribs_te_orientation_angles',
        # Horizontal tail leading edge riblets inputs
        'ht_n_ribs_le',
        'ht_ribs_le_spanwise_reference_spars_idx',
        'ht_ribs_le_spanwise_positions',
        'ht_ribs_le_orientation_reference_spars',
        'ht_ribs_le_orientation_angles',
        # Horizontal tail fuel tanks inputs
        'ht_fuel_tank_boundaries',
        # Horizontal tail movables inputs
        'ht_n_movables',
        'ht_movable_spanwise_starts', 'ht_movable_spanwise_ends',
        'ht_movable_hingeline_starts', 'ht_movable_deflections',
        'ht_movables_symmetric',
        # Horizontal tail engines inputs
        'ht_n_engines',
        'ht_engine_spanwise_positions', 'ht_engine_overhangs',
        'ht_engine_thrusts',
        'ht_engine_specific_fuel_consumptions',
        # Vertical tail inputs ----------------------------------------------
        # Positioning
        'vertical_tail_trans_pos',
        # Vertical tail wing segments inputs
        'vt_n_wing_segments',
        'vt_airfoil_names', 'vt_chords', 'vt_twists',
        'vt_sweeps_le', 'vt_dihedral_angles', 'vt_spanwise_positions',
        'vt_semi_span', 'vt_wing_cant',
        # Vertical tail spars inputs
        'vt_n_spars',
        'vt_spar_chordwise_positions', 'vt_spar_aspect_ratios',
        'vt_spar_profiles', 'vt_spar_spanwise_positions_end',
        # Vertical tail box ribs inputs
        'vt_n_ribs_wb',
        'vt_ribs_wb_spanwise_reference_spars_idx',
        'vt_ribs_wb_spanwise_positions',
        'vt_ribs_wb_orientation_reference_spars',
        'vt_ribs_wb_orientation_angles',
        # Vertical tail trailing edge riblets inputs
        'vt_n_ribs_te',
        'vt_ribs_te_spanwise_reference_spars_idx',
        'vt_ribs_te_spanwise_positions',
        'vt_ribs_te_orientation_reference_spars',
        'vt_ribs_te_orientation_angles',
        # Vertical tail leading edge riblets inputs
        'vt_n_ribs_le',
        'vt_ribs_le_spanwise_reference_spars_idx',
        'vt_ribs_le_spanwise_positions',
        'vt_ribs_le_orientation_reference_spars',
        'vt_ribs_le_orientation_angles',
        # Vertical tail fuel tanks inputs
        'vt_fuel_tank_boundaries',
        # Vertical tail movables inputs
        'vt_n_movables',
        'vt_movable_spanwise_starts', 'vt_movable_spanwise_ends',
        'vt_movable_hingeline_starts', 'vt_movable_deflections',
        'vt_movables_symmetric',
        # Vertical tail engines inputs
        'vt_n_engines',
        'vt_engine_spanwise_positions', 'vt_engine_overhangs',
        'vt_engine_thrusts',
        'vt_engine_specific_fuel_consumptions'
    ]

    # Optional inputs
    name = Input('aircraft')
    color = Input('white')
    transparency = Input(0.5)
    avl_CL_start = Input(0.0)
    avl_CL_end = Input(1.1)
    avl_CL_step = Input(0.25)
    avl_delta_e_start = Input(-40.)
    avl_delta_e_end = Input(41.)
    avl_delta_e_step = Input(20.)
    convergence_tol = Input(1e-4)

    @Part
    def fuselage(self):
        return Fuselage(
            map_down=['fuselage_diameter->diameter',
                      'fuselage_tail_angle->tail_angle',
                      'fuselage_tail_length->tail_length',
                      'fuselage_cockpit_length->cockpit_length',
                      'fuselage_cabin_length->cabin_length',
                      'fuselage_nose_length->nose_length'],
            position=self.position)

    @Part
    def main_wing_starboard(self):
        return Wing(
            name='main_wing_starboard',
            location=self.fuselage.point_at_fractions(
                self.main_wing_long_pos,
                self.main_wing_trans_pos,
                self.main_wing_lat_pos),
            map_down=[
                # Wing segments inputs
                'mw_n_wing_segments->n_wing_segments',
                'mw_airfoil_names->airfoil_names',
                'mw_chords->chords', 'mw_twists->twists',
                'mw_sweeps_le->sweeps_le',
                'mw_dihedral_angles->dihedral_angles',
                'mw_spanwise_positions->spanwise_positions',
                'mw_semi_span->semi_span', 'mw_wing_cant->wing_cant',
                # Spars inputs
                'mw_n_spars->n_spars',
                'mw_spar_chordwise_positions->spar_chordwise_positions',
                'mw_spar_aspect_ratios->spar_aspect_ratios',
                'mw_spar_profiles->spar_profiles',
                'mw_spar_spanwise_positions_end->spar_spanwise_positions_end',
                # Wing box ribs inputs
                'mw_n_ribs_wb->n_ribs_wb',
                'mw_ribs_wb_spanwise_reference_spars_idx->'
                'ribs_wb_spanwise_reference_spars_idx',
                'mw_ribs_wb_spanwise_positions->ribs_wb_spanwise_positions',
                'mw_ribs_wb_orientation_reference_spars->'
                'ribs_wb_orientation_reference_spars',
                'mw_ribs_wb_orientation_angles->ribs_wb_orientation_angles',
                # Trailing edge riblets inputs
                'mw_n_ribs_te->n_ribs_te',
                'mw_ribs_te_spanwise_reference_spars_idx->'
                'ribs_te_spanwise_reference_spars_idx',
                'mw_ribs_te_spanwise_positions->ribs_te_spanwise_positions',
                'mw_ribs_te_orientation_reference_spars->'
                'ribs_te_orientation_reference_spars',
                'mw_ribs_te_orientation_angles->ribs_te_orientation_angles',
                # Leading edge riblets inputs
                'mw_n_ribs_le->n_ribs_le',
                'mw_ribs_le_spanwise_reference_spars_idx->'
                'ribs_le_spanwise_reference_spars_idx',
                'mw_ribs_le_spanwise_positions->ribs_le_spanwise_positions',
                'mw_ribs_le_orientation_reference_spars->'
                'ribs_le_orientation_reference_spars',
                'mw_ribs_le_orientation_angles->ribs_le_orientation_angles',
                # Fuel tank inputs
                'mw_fuel_tank_boundaries->fuel_tank_boundaries',
                # Movables inputs
                'mw_n_movables->n_movables',
                'mw_movable_spanwise_starts->movable_spanwise_starts',
                'mw_movable_spanwise_ends->movable_spanwise_ends',
                'mw_movable_hingeline_starts->movable_hingeline_starts',
                'mw_movable_deflections->movable_deflections',
                'mw_movables_symmetric->movables_symmetric',
                'mw_movables_names->movables_names',
                # Engines inputs
                'mw_n_engines->n_engines',
                'mw_engine_spanwise_positions->engine_spanwise_positions',
                'mw_engine_overhangs->engine_overhangs',
                'mw_engine_thrusts->engine_thrusts',
                'mw_engine_specific_fuel_consumptions'
                '->engine_specific_fuel_consumptions',
                'mw_engine_diameters_inlet->engine_diameters_inlet',
                'mw_engine_diameters_outlet->engine_diameters_outlet',
                'mw_engine_diameters_part2->engine_diameters_part2',
                'mw_engine_length_cones1->engine_length_cones1',
                'mw_engine_length_cones2->engine_length_cones2'
                ]
        )

    @Part
    def main_wing_port(self):
        return Wing(
            name='main_wing_port',
            is_starboard=False,
            location=self.fuselage.point_at_fractions(
                self.main_wing_long_pos,
                self.main_wing_trans_pos,
                -self.main_wing_lat_pos),
            map_down=[
                # Wing segments inputs
                'mw_n_wing_segments->n_wing_segments',
                'mw_airfoil_names->airfoil_names',
                'mw_chords->chords', 'mw_twists->twists',
                'mw_sweeps_le->sweeps_le',
                'mw_dihedral_angles->dihedral_angles',
                'mw_spanwise_positions->spanwise_positions',
                'mw_semi_span->semi_span', 'mw_wing_cant->wing_cant',
                # Spars inputs
                'mw_n_spars->n_spars',
                'mw_spar_chordwise_positions->spar_chordwise_positions',
                'mw_spar_aspect_ratios->spar_aspect_ratios',
                'mw_spar_profiles->spar_profiles',
                'mw_spar_spanwise_positions_end->spar_spanwise_positions_end',
                # Wing box ribs inputs
                'mw_n_ribs_wb->n_ribs_wb',
                'mw_ribs_wb_spanwise_reference_spars_idx->'
                'ribs_wb_spanwise_reference_spars_idx',
                'mw_ribs_wb_spanwise_positions->ribs_wb_spanwise_positions',
                'mw_ribs_wb_orientation_reference_spars->'
                'ribs_wb_orientation_reference_spars',
                'mw_ribs_wb_orientation_angles->ribs_wb_orientation_angles',
                # Trailing edge riblets inputs
                'mw_n_ribs_te->n_ribs_te',
                'mw_ribs_te_spanwise_reference_spars_idx->'
                'ribs_te_spanwise_reference_spars_idx',
                'mw_ribs_te_spanwise_positions->ribs_te_spanwise_positions',
                'mw_ribs_te_orientation_reference_spars->'
                'ribs_te_orientation_reference_spars',
                'mw_ribs_te_orientation_angles->ribs_te_orientation_angles',
                # Leading edge riblets inputs
                'mw_n_ribs_le->n_ribs_le',
                'mw_ribs_le_spanwise_reference_spars_idx->'
                'ribs_le_spanwise_reference_spars_idx',
                'mw_ribs_le_spanwise_positions->ribs_le_spanwise_positions',
                'mw_ribs_le_orientation_reference_spars->'
                'ribs_le_orientation_reference_spars',
                'mw_ribs_le_orientation_angles->ribs_le_orientation_angles',
                # Fuel tank inputs
                'mw_fuel_tank_boundaries->fuel_tank_boundaries',
                # Movables inputs
                'mw_n_movables->n_movables',
                'mw_movable_spanwise_starts->movable_spanwise_starts',
                'mw_movable_spanwise_ends->movable_spanwise_ends',
                'mw_movable_hingeline_starts->movable_hingeline_starts',
                'mw_movable_deflections->movable_deflections',
                'mw_movables_symmetric->movables_symmetric',
                'mw_movables_names->movables_names',
                # Engines inputs
                'mw_n_engines->n_engines',
                'mw_engine_spanwise_positions->engine_spanwise_positions',
                'mw_engine_overhangs->engine_overhangs',
                'mw_engine_thrusts->engine_thrusts',
                'mw_engine_specific_fuel_consumptions'
                '->engine_specific_fuel_consumptions',
                'mw_engine_diameters_inlet->engine_diameters_inlet',
                'mw_engine_diameters_outlet->engine_diameters_outlet',
                'mw_engine_diameters_part2->engine_diameters_part2',
                'mw_engine_length_cones1->engine_length_cones1',
                'mw_engine_length_cones2->engine_length_cones2'
            ]
        )

    @Part
    def vertical_tail(self):
        return Wing(
            name='vertical_tail',
            wing_cant=90.,
            location=translate(self.fuselage.end, 'x_', self.vt_chords[0]),
            is_starboard=False,
            map_down=[
                # Wing segments inputs
                'vt_n_wing_segments->n_wing_segments',
                'vt_airfoil_names->airfoil_names',
                'vt_chords->chords', 'vt_twists->twists',
                'vt_sweeps_le->sweeps_le',
                'vt_dihedral_angles->dihedral_angles',
                'vt_spanwise_positions->spanwise_positions',
                'vt_semi_span->semi_span', 'vt_wing_cant->wing_cant',
                # Spars inputs
                'vt_n_spars->n_spars',
                'vt_spar_chordwise_positions->spar_chordwise_positions',
                'vt_spar_aspect_ratios->spar_aspect_ratios',
                'vt_spar_profiles->spar_profiles',
                'vt_spar_spanwise_positions_end->spar_spanwise_positions_end',
                # Wing box ribs inputs
                'vt_n_ribs_wb->n_ribs_wb',
                'vt_ribs_wb_spanwise_reference_spars_idx->'
                'ribs_wb_spanwise_reference_spars_idx',
                'vt_ribs_wb_spanwise_positions->ribs_wb_spanwise_positions',
                'vt_ribs_wb_orientation_reference_spars->'
                'ribs_wb_orientation_reference_spars',
                'vt_ribs_wb_orientation_angles->ribs_wb_orientation_angles',
                # Trailing edge riblets inputs
                'vt_n_ribs_te->n_ribs_te',
                'vt_ribs_te_spanwise_reference_spars_idx->'
                'ribs_te_spanwise_reference_spars_idx',
                'vt_ribs_te_spanwise_positions->ribs_te_spanwise_positions',
                'vt_ribs_te_orientation_reference_spars->'
                'ribs_te_orientation_reference_spars',
                'vt_ribs_te_orientation_angles->ribs_te_orientation_angles',
                # Leading edge riblets inputs
                'vt_n_ribs_le->n_ribs_le',
                'vt_ribs_le_spanwise_reference_spars_idx->'
                'ribs_le_spanwise_reference_spars_idx',
                'vt_ribs_le_spanwise_positions->ribs_le_spanwise_positions',
                'vt_ribs_le_orientation_reference_spars->'
                'ribs_le_orientation_reference_spars',
                'vt_ribs_le_orientation_angles->ribs_le_orientation_angles',
                # Fuel tank inputs
                'vt_fuel_tank_boundaries->fuel_tank_boundaries',
                # Movables inputs
                'vt_n_movables->n_movables',
                'vt_movable_spanwise_starts->movable_spanwise_starts',
                'vt_movable_spanwise_ends->movable_spanwise_ends',
                'vt_movable_hingeline_starts->movable_hingeline_starts',
                'vt_movable_deflections->movable_deflections',
                'vt_movables_symmetric->movables_symmetric',
                'vt_movables_names->movables_names',
                # Engines inputs
                'vt_n_engines->n_engines',
                'vt_engine_spanwise_positions->engine_spanwise_positions',
                'vt_engine_overhangs->engine_overhangs',
                'vt_engine_thrusts->engine_thrusts',
                'vt_engine_specific_fuel_consumptions'
                '->engine_specific_fuel_consumptions',
                'vt_engine_diameters_inlet->engine_diameters_inlet',
                'vt_engine_diameters_outlet->engine_diameters_outlet',
                'vt_engine_diameters_part2->engine_diameters_part2',
                'vt_engine_length_cones1->engine_length_cones1',
                'vt_engine_length_cones2->engine_length_cones2'
            ]
        )

    @Part
    def horizontal_tail_starboard(self):
        return Wing(
            name='horizontal_tail_starboard',
            location=translate(self.fuselage.point_at_fractions(
                1.,
                self.horizontal_tail_trans_pos,
                self.horizontal_tail_lat_pos
            ), self.position.Vx_, self.ht_chords[0])
            if self.tail_type == 'conventional'
            else self.vertical_tail.sections[-1].position.location,
            map_down=[
                # Wing segments inputs
                'ht_n_wing_segments->n_wing_segments',
                'ht_airfoil_names->airfoil_names',
                'ht_chords->chords', 'ht_twists->twists',
                'ht_sweeps_le->sweeps_le',
                'ht_dihedral_angles->dihedral_angles',
                'ht_spanwise_positions->spanwise_positions',
                'ht_semi_span->semi_span', 'ht_wing_cant->wing_cant',
                # Spars inputs
                'ht_n_spars->n_spars',
                'ht_spar_chordwise_positions->spar_chordwise_positions',
                'ht_spar_aspect_ratios->spar_aspect_ratios',
                'ht_spar_profiles->spar_profiles',
                'ht_spar_spanwise_positions_end->spar_spanwise_positions_end',
                # Wing box ribs inputs
                'ht_n_ribs_wb->n_ribs_wb',
                'ht_ribs_wb_spanwise_reference_spars_idx->'
                'ribs_wb_spanwise_reference_spars_idx',
                'ht_ribs_wb_spanwise_positions->ribs_wb_spanwise_positions',
                'ht_ribs_wb_orientation_reference_spars->'
                'ribs_wb_orientation_reference_spars',
                'ht_ribs_wb_orientation_angles->ribs_wb_orientation_angles',
                # Trailing edge riblets inputs
                'ht_n_ribs_te->n_ribs_te',
                'ht_ribs_te_spanwise_reference_spars_idx->'
                'ribs_te_spanwise_reference_spars_idx',
                'ht_ribs_te_spanwise_positions->ribs_te_spanwise_positions',
                'ht_ribs_te_orientation_reference_spars->'
                'ribs_te_orientation_reference_spars',
                'ht_ribs_te_orientation_angles->ribs_te_orientation_angles',
                # Leading edge riblets inputs
                'ht_n_ribs_le->n_ribs_le',
                'ht_ribs_le_spanwise_reference_spars_idx->'
                'ribs_le_spanwise_reference_spars_idx',
                'ht_ribs_le_spanwise_positions->ribs_le_spanwise_positions',
                'ht_ribs_le_orientation_reference_spars->'
                'ribs_le_orientation_reference_spars',
                'ht_ribs_le_orientation_angles->ribs_le_orientation_angles',
                # Fuel tank inputs
                'ht_fuel_tank_boundaries->fuel_tank_boundaries',
                # Movables inputs
                'ht_n_movables->n_movables',
                'ht_movable_spanwise_starts->movable_spanwise_starts',
                'ht_movable_spanwise_ends->movable_spanwise_ends',
                'ht_movable_hingeline_starts->movable_hingeline_starts',
                'ht_movable_deflections->movable_deflections',
                'ht_movables_symmetric->movables_symmetric',
                'ht_movables_names->movables_names',
                # Engines inputs
                'ht_n_engines->n_engines',
                'ht_engine_spanwise_positions->engine_spanwise_positions',
                'ht_engine_overhangs->engine_overhangs',
                'ht_engine_thrusts->engine_thrusts',
                'ht_engine_specific_fuel_consumptions'
                '->engine_specific_fuel_consumptions',
                'ht_engine_diameters_inlet->engine_diameters_inlet',
                'ht_engine_diameters_outlet->engine_diameters_outlet',
                'ht_engine_diameters_part2->engine_diameters_part2',
                'ht_engine_length_cones1->engine_length_cones1',
                'ht_engine_length_cones2->engine_length_cones2'
            ]
        )

    @Part
    def horizontal_tail_port(self):
        return Wing(
            name='horizontal_tail_port',
            is_starboard=False,
            location=translate(self.fuselage.point_at_fractions(
                1.,
                self.horizontal_tail_trans_pos,
                -self.horizontal_tail_lat_pos
            ), self.position.Vx_, self.ht_chords[0])
            if self.tail_type == 'conventional'
            else self.vertical_tail.sections[-1].position.location,
            map_down=[
                # Wing segments inputs
                'ht_n_wing_segments->n_wing_segments',
                'ht_airfoil_names->airfoil_names',
                'ht_chords->chords', 'ht_twists->twists',
                'ht_sweeps_le->sweeps_le',
                'ht_dihedral_angles->dihedral_angles',
                'ht_spanwise_positions->spanwise_positions',
                'ht_semi_span->semi_span', 'ht_wing_cant->wing_cant',
                # Spars inputs
                'ht_n_spars->n_spars',
                'ht_spar_chordwise_positions->spar_chordwise_positions',
                'ht_spar_aspect_ratios->spar_aspect_ratios',
                'ht_spar_profiles->spar_profiles',
                'ht_spar_spanwise_positions_end->spar_spanwise_positions_end',
                # Wing box ribs inputs
                'ht_n_ribs_wb->n_ribs_wb',
                'ht_ribs_wb_spanwise_reference_spars_idx->'
                'ribs_wb_spanwise_reference_spars_idx',
                'ht_ribs_wb_spanwise_positions->ribs_wb_spanwise_positions',
                'ht_ribs_wb_orientation_reference_spars->'
                'ribs_wb_orientation_reference_spars',
                'ht_ribs_wb_orientation_angles->ribs_wb_orientation_angles',
                # Trailing edge riblets inputs
                'ht_n_ribs_te->n_ribs_te',
                'ht_ribs_te_spanwise_reference_spars_idx->'
                'ribs_te_spanwise_reference_spars_idx',
                'ht_ribs_te_spanwise_positions->ribs_te_spanwise_positions',
                'ht_ribs_te_orientation_reference_spars->'
                'ribs_te_orientation_reference_spars',
                'ht_ribs_te_orientation_angles->ribs_te_orientation_angles',
                # Leading edge riblets inputs
                'ht_n_ribs_le->n_ribs_le',
                'ht_ribs_le_spanwise_reference_spars_idx->'
                'ribs_le_spanwise_reference_spars_idx',
                'ht_ribs_le_spanwise_positions->ribs_le_spanwise_positions',
                'ht_ribs_le_orientation_reference_spars->'
                'ribs_le_orientation_reference_spars',
                'ht_ribs_le_orientation_angles->ribs_le_orientation_angles',
                # Fuel tank inputs
                'ht_fuel_tank_boundaries->fuel_tank_boundaries',
                # Movables inputs
                'ht_n_movables->n_movables',
                'ht_movable_spanwise_starts->movable_spanwise_starts',
                'ht_movable_spanwise_ends->movable_spanwise_ends',
                'ht_movable_hingeline_starts->movable_hingeline_starts',
                'ht_movable_deflections->movable_deflections',
                'ht_movables_symmetric->movables_symmetric',
                'ht_movables_names->movables_names',
                # Engines inputs
                'ht_n_engines->n_engines',
                'ht_engine_spanwise_positions->engine_spanwise_positions',
                'ht_engine_overhangs->engine_overhangs',
                'ht_engine_thrusts->engine_thrusts',
                'ht_engine_specific_fuel_consumptions'
                '->engine_specific_fuel_consumptions',
                'ht_engine_diameters_inlet->engine_diameters_inlet',
                'ht_engine_diameters_outlet->engine_diameters_outlet',
                'ht_engine_diameters_part2->engine_diameters_part2',
                'ht_engine_length_cones1->engine_length_cones1',
                'ht_engine_length_cones2->engine_length_cones2'
            ]
        )

    @Part
    def STEPWriter(self):
        return STEPWriter(trees=[self],
                          default_directory=os.path.join(os.getcwd(),
                                                         'output',
                                                         'file.stp'))

    @Part
    def scissor_plot(self):
        return ScissorPlot(
            CL_0=self.main_wing_starboard.CL_0,
            Cm_0=self.main_wing_starboard.Cm_0,
            CL_alpha_wing=math.degrees(self.main_wing_starboard.CL_alpha),
            CL_alpha_horizontal=math.degrees(self.horizontal_tail_starboard
                                             .CL_alpha),
            sweep_angle_025c=math.radians(self.main_wing_starboard
                                          .sweep_c_over_4),
            fuselage_diameter=self.fuselage.diameter,
            fuselage_length=self.fuselage.length,
            mac=self.main_wing_starboard.mean_aerodynamic_chord,
            span=self.mw_span,
            aspect_ratio=self.aspect_ratio,
            stability_margin=self.stability_margin,
            wing_area=self.wing_area,
            net_wing_area=self.net_wing_area,
            l_h=self.l_h,
            z_h=self.z_h,
            x_ac=self.x_ac_wing_fus,
            CL_alpha_a_h=self.Cl_alpha_a_h,
            tail_type=self.tail_type,
            forward_cg=self.forward_cg,
            aft_cg=self.aft_cg
        )

    @Attribute
    def symmetry_plane(self):
        return Plane(self.position, self.position.Vy, self.position.Vx)

    @Attribute
    def MTOM(self):
        mw_fuel = 2. * sum(
            tank.fuel.initial_mass
            for tank in self.main_wing_starboard.fuel_tanks
        )
        ht_fuel = 2. * sum(
            tank.fuel.initial_mass
            for tank in self.horizontal_tail_starboard.fuel_tanks
        )
        vt_fuel = sum(
            tank.fuel.initial_mass for tank in self.vertical_tail.fuel_tanks
        )
        return self.ZFM + mw_fuel + ht_fuel + vt_fuel

    @Attribute
    def wing_area(self):
        """ Return the wing area.

        :rtype: float
        """
        return sum([self.main_wing_starboard.reference_area,
                    self.main_wing_port.reference_area])

    @Attribute
    def mean_aerodynamic_chord(self):
        return self.main_wing_starboard.mean_aerodynamic_chord

    @Attribute
    def mac_position(self):
        return Point(self.main_wing_starboard.mac_position.x,
                     0.,
                     self.main_wing_starboard.mac_position.z)

    @Attribute
    def aspect_ratio(self):
        """ The overall aspect / slenderness ratio of the wing.

        :rtype: float
        """
        return self.mw_span ** 2 / self.wing_area

    @Part
    def avl_analysis(self):
        """ The AVL analysis wrapper part.
        """
        return avl.Interface(cases=self.cases,
                             configuration=self.avl_configuration)

    @Attribute
    def avl_configuration(self):
        """ The avl configuration of this aircraft, such that it can be
        interpreted by AVL.
        """
        return avl.Configuration(
            name=self.name,
            surfaces=[self.main_wing_starboard.avl_surface,
                      self.horizontal_tail_starboard.avl_surface,
                      self.vertical_tail.avl_surface],
            mach=self.mach,
            reference_area=self.wing_area,
            reference_chord=self.main_wing_starboard.mean_aerodynamic_chord,
            reference_span=self.mw_span,
            reference_point=self.mac_position
            )

    @Attribute
    def avl_configuration_less_tail(self):
        """ The avl configuration of this aircraft without tail, such that it
        can be interpreted by AVL.
        """
        # TODO: add fuselage body
        return avl.Configuration(
            name=self.name,
            surfaces=[self.main_wing_starboard.avl_surface],
            mach=self.mach,
            reference_area=self.wing_area,
            reference_chord=self.main_wing_starboard.mean_aerodynamic_chord,
            reference_span=self.mw_span,
            reference_point=Point(self.main_wing_starboard.mac_position.x,
                                  0.,
                                  self.main_wing_starboard.mac_position.z)
            )

    @Attribute
    def cases(self):
        return [avl.Case(name='CL_{:.1f}_delta_e_{:.1f}'.format(CL, delta_e),
                         settings={'alpha': avl.Parameter(name='alpha',
                                                          value=CL,
                                                          constraint='CL'),
                                   'elevator': delta_e})
                for CL in np.arange(self.avl_CL_start,
                                    self.avl_CL_end,
                                    self.avl_CL_step)
                for delta_e in np.arange(self.avl_delta_e_start,
                                         self.avl_delta_e_end,
                                         self.avl_delta_e_step)]

    @Attribute
    def net_wing_area(self):
        """ Return the net wing area of the wing portion that sticks out of
        the fuselage.

        :rtype: float
        """
        net_semi_wing = Subtracted(self.main_wing_starboard.planform,
                                   self.fuselage.solid)
        return 2. * sum(fce.area for fce in net_semi_wing.faces)

    @Attribute
    def net_root_le_point(self):
        """ Return the root leading edge point of the portion of the wing
        that sticks out of the fuselage.

        :rtype: float
        """
        net_semi_wing = Subtracted(self.main_wing_starboard.planform,
                                   self.fuselage.solid)
        vrtex = min(net_semi_wing.vertices,
                    key=lambda v: (v.point.distance(self.main_wing_starboard
                                                    .sections[0].position)))
        return vrtex.point

    @Attribute
    def x_ac_wing_fus(self):
        """ Calculates the position of the aerodynamic centre with respect
        to the position of the mac. The contributions are the engines,
        the wing and the fuselage.

        :rtype: float
        """
        wing = self.main_wing_starboard
        width_nacelle = self.mw_engine_diameters_inlet
        x_ac_engines = sum(-4.0 * width_nacelle[idx] ** 2
                           * self.distance_nacelle_mac[idx] /
                           (self.wing_area * wing.mean_aerodynamic_chord *
                            self.Cl_alpha_a_h)
                           for idx in range(self.mw_n_engines / 2))
        x_ac_wing = 0.25
        l_nose_le = self.net_root_le_point.x - self.position.x
        mac = self.main_wing_starboard.mean_aerodynamic_chord
        x_ac_rest_1 = -1.8 / self.Cl_alpha_a_h * self.fuselage_diameter ** 2 \
            * l_nose_le / (self.wing_area * mac)
        x_ac_rest_2 = 0.273 / (1 + wing.taper_ratio) * (
                self.wing_area / self.mw_span) * self.fuselage_diameter * (
                              self.mw_span - self.fuselage_diameter) / \
            (mac ** 2 * (self.mw_span + 2.15 * self.fuselage_diameter)) \
            * math.tan(math.radians(wing.sweep_c_over_4))
        return x_ac_wing + x_ac_rest_1 + x_ac_rest_2 + x_ac_engines

    @Attribute
    def Cl_alpha_a_h(self):
        """ Calculates the Lift curve coefficient of the fuselage wing body.
        This is the aircraft with fuselage and wing without horizontal
        tailplane.
        :rtype: float
        """
        cl_alpha_wing = math.degrees(self.main_wing_starboard.CL_alpha)
        # TODO: CL_alpha a_h (main wings + fuselage uit AVL halen.
        gradient_rad = cl_alpha_wing * (
                1 + 2.15 * self.fuselage_diameter / self.mw_span) \
            * self.net_wing_area / self.wing_area + math.pi / 2. * \
            self.fuselage_diameter ** 2 \
            / self.wing_area
        return gradient_rad

    @Attribute
    def distance_nacelle_mac(self):
        return [self.main_wing_starboard.mac_position.x - engine.position.x
                for engine in self.main_wing_starboard.engines]

    @Attribute
    def l_h(self):
        return self.horizontal_tail_starboard.mac_position.x - (
            self.main_wing_starboard.x_lemac + self.x_ac_wing_fus *
            self.main_wing_starboard.mean_aerodynamic_chord
        )

    @Attribute
    def l_v(self):
        return self.vertical_tail.mac_position.x - (
            self.main_wing_starboard.x_lemac + self.x_ac_wing_fus *
            self.main_wing_starboard.mean_aerodynamic_chord
        )

    @Attribute
    def z_h(self):
        return self.horizontal_tail_starboard.position.z - \
               self.main_wing_starboard.position.z

    @Attribute
    def CL(self):
        weight = self.mass * self.g0
        rho = self.air_density
        v = self.velocity
        s = self.wing_area
        return weight / (0.5 * rho * v ** 2 * s)

    @Attribute
    def empty_cog(self):
        """ Return the cog position of the aircraft without fuel.

        :rtype: parapy.geom.generic.positioning.Point
        """
        wings = [self.main_wing_starboard, self.main_wing_port,
                 self.horizontal_tail_starboard, self.horizontal_tail_port,
                 self.vertical_tail]
        engines = [engine for wing in wings[:2] for engine in wing.engines]
        empty_mass = sum(wing.mass for wing in wings) +\
            sum(engine.mass for engine in engines) + self.fuselage.mass
        empty_mass_moment = self.fuselage.mass * np.array(self.fuselage.cog) +\
            sum(engine.mass * np.array(engine.cog) for engine in engines) +\
            sum(wing.mass * np.array(wing.cog) for wing in wings)
        return Point(*empty_mass_moment / empty_mass)

    @Attribute
    def full_cog(self):
        """ Return the cog position of the aircraft with max. fuel.

        :rtype: parapy.geom.generic.positioning.Point
        """
        cog_full = (self.ZFM * np.array(self.empty_cog) +
                    self.max_fuel_mass * np.array(self.max_fuel_cog)) / \
            self.MTOM

        return Point(*cog_full)

    @Attribute
    def cog(self):
        """ Return the current cog position of the aircraft.

        :rtype: parapy.geom.generic.positioning.Point
        """
        cog = (self.ZFM * np.array(self.empty_cog) +
               self.fuel_mass * np.array(self.fuel_cog)) / self.mass

        return Point(*cog)

    @Attribute
    def mass(self):
        """ Return the current mass of the aircraft.

        :rtype: float
        """
        return self.ZFM + self.fuel_mass

    @Attribute
    def max_fuel_mass(self):
        """ Return the maximum fuel mass that can be carried by this aircraft.

        :rtype: float
        """
        return sum(tank.fuel.initial_mass
                   for _child in self.children if hasattr(_child, 'fuel_tanks')
                   for tank in _child.fuel_tanks if tank.is_used)

    @Attribute
    def max_fuel_cog(self):
        """ Return the position of the centre of gravity of the fuel,
        when the aircraft is at maximum fuel capacity.

        :rtype: parapy.geom.generic.positioning.Point
        """
        first_moment_of_mass = sum(
            tank.fuel.initial_mass * np.array(tank.solid.cog)
            for _child in self.children if hasattr(_child, 'fuel_tanks')
            for tank in _child.fuel_tanks if tank.is_used
        )
        return Point(*first_moment_of_mass / self.max_fuel_mass)

    @Attribute
    def fuel_mass(self):
        """ Return the current fuel mass that is carried by this aircraft.

        :rtype: float
        """
        return sum(tank.fuel.mass
                   for _child in self.children if hasattr(_child, 'fuel_tanks')
                   for tank in _child.fuel_tanks if not tank.is_empty)

    @Attribute
    def fuel_cog(self):
        """ Return the current position of the centre of gravity of the fuel.

        :rtype: parapy.geom.generic.positioning.Point
        """
        first_moment_of_mass = sum(tank.fuel.mass * np.array(tank.fuel.cog)
                                   for _child in self.children
                                   if hasattr(_child, 'fuel_tanks')
                                   for tank in _child.fuel_tanks
                                   if not tank.is_empty)
        if self.fuel_mass <= 0.:
            return ORIGIN
        else:
            return Point(*first_moment_of_mass / self.fuel_mass)

    @Attribute
    def forward_cg(self):
        """ The most forward position of the center of gravity, expressed as a
        fraction of the mean aerodynamic chord.

        :rtype: float
        """
        forward_cg = min([self.full_cog, self.empty_cog], key=lambda pt: pt.x)
        return (forward_cg.x - self.main_wing_starboard.x_lemac) / \
            self.main_wing_starboard.mean_aerodynamic_chord

    @Attribute
    def aft_cg(self):
        """ The most rearward position of the center of gravity, expressed
        as a fraction of the mean aerodynamic chord.

        :rtype: float
        """
        rear_cg = max([self.full_cog, self.empty_cog], key=lambda pt: pt.x)
        return (rear_cg.x - self.main_wing_starboard.x_lemac) / \
            self.main_wing_starboard.mean_aerodynamic_chord

    def trim(self, max_iter=50):
        """ Trim the aircraft by deflecting the elevator in such a way that
        the aerodynamic moments balance the aircraft weight-induced moments.
        Returns the required elevator deflection for trim conditions.

        :rtype: float
        """
        # Take all the moments around the nose of the aircraft.
        arm = self.cog - self.position
        weight_cm = self.CL * arm.x / self.mean_aerodynamic_chord

        convergence_error = np.inf
        interval = [self.avl_delta_e_start, self.avl_delta_e_end]
        n_iter = 0

        while convergence_error > self.convergence_tol and n_iter <= max_iter:
            # Set the elevator deflection to the midpoint of the interval
            delta_e = sum(interval) / len(interval)
            aero_cm = self.get_Cm(self.CL, delta_e)
            if weight_cm + aero_cm > 0:
                # If the weight moment outweighs the aerodynamic moment
                interval = [delta_e, interval[-1]]
            else:
                interval = [interval[0], delta_e]

            convergence_error = abs(weight_cm + aero_cm)

            n_iter += 1

        return delta_e

    def get_alpha(self, CL, delta_e):
        """ Return the drag coefficient for a given alpha (angle
        of attack) and delta_e (elevator deflection).

        :param CL: lift coefficient
        :type CL: float | int

        :param delta_e: elevator deflection in degrees
        :type delta_e: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: float
        """
        return self.get_quantity('Alpha', CL, delta_e)

    def get_Cm(self, CL, delta_e):
        """ Return the pitching moment coefficient for a given alpha (angle
        of attack) and delta_e (elevator deflection).

        :param CL: lift coefficient
        :type CL: float | int

        :param delta_e: elevator deflection in degrees
        :type delta_e: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: float
        """
        return self.get_quantity('Cmtot', CL, delta_e)

    def get_CD(self, CL, delta_e):
        """ Return the drag coefficient for a given alpha (angle
        of attack) and delta_e (elevator deflection).

        :param CL: lift coefficient
        :type CL: float | int

        :param delta_e: elevator deflection in degrees
        :type delta_e: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: float
        """
        return self.get_quantity('CDtot', CL, delta_e)

    def get_quantity(self, quantity, CL, delta_e):
        """ Return any AVL 'total' quantity for a given alpha (angle
        of attack) and delta_e (elevator deflection).

        :param quantity: the quantity that is requested
        :type quantity: str

        :param CL: lift coefficient
        :type CL: float | int

        :param delta_e: elevator deflection in degrees
        :type delta_e: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: numpy.ndarray[float]
        """
        if not self.avl_CL_start <= CL <= self.avl_CL_end:
            raise Exception(
                'The requested {} for alpha: {} is out of the range of '
                'alpha_start: {} and alpha_end: {}. '
                'Extrapolation is not supported.'
                .format(quantity, CL, self.avl_CL_start, self.avl_CL_end)
            )
        if not self.avl_delta_e_start <= delta_e <= self.avl_delta_e_end:
            raise Exception(
                'The requested {} for alpha: {} is out of the range of '
                'alpha_start: {} and alpha_end: {}. '
                'Extrapolation is not supported.'
                .format(quantity, delta_e,
                        self.avl_delta_e_start, self.avl_delta_e_end)
            )

        CLs = np.arange(self.avl_CL_start, self.avl_CL_end, self.avl_CL_step)

        delta_es = np.arange(self.avl_delta_e_start, self.avl_delta_e_end,
                             self.avl_delta_e_step)
        values = [[self.avl_analysis.results['CL_{:.1f}_delta_e_{:.1f}'
                   .format(float(_CL), float(_delta_e))]['Totals'][quantity]
                   for _CL in CLs]
                  for _delta_e in delta_es]

        f = interpolate.interp2d(CLs, delta_es, values, bounds_error=True)

        return f(CL, delta_e)

    def get_custom_avl_results(self, alpha, show_trefftz_plot=False,
                               show_geometry=False, **kwargs):
        """ Get avl results for a custom set of case parameters. Using
        ``**kwargs``, the elevator, aileron, or flap deflections can be set,
        or any other movable that has been properly defined with a name.

        .. note::
           Trying to show the trefftz plot or the geometry in AVL is known
           to crash often, when run from the Python console.

        :param alpha: the angle of attack of the configuration.
        :type alpha: float
        :param show_trefftz_plot: show the trefftz plot?
        :type show_trefftz_plot: bool
        :param show_geometry: show the wing geometry?
        :type show_geometry: bool
        :param kwargs: a (set of) key-value pair(s) defining a (set of)
            movable deflection(s).

        """
        settings = {'alpha': avl.Parameter(name='alpha', value=alpha)}
        settings.update(kwargs)

        cases = [avl.Case(name='custom', settings=settings)]

        analysis = avl.Interface(cases=cases,
                                 configuration=self.avl_configuration)
        if show_trefftz_plot:
            analysis.show_trefftz_plot()
        if show_geometry:
            analysis.show_geometry()
        return analysis.results['custom']


if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft(
        # Aircraft weights
        ZFM=50000., fuel_fraction=0.4,
        # Cruise flight parameters
        velocity=235.,
        mach=0.8,
        reynolds=1000000,
        air_density=0.35,
        ult_load_factor=1.5 * 2.5,
        g0=9.80665,
        # Stability inputs
        stability_margin=0.05,
        # Tail configuration inputs
        tail_type='conventional',
        # Fuselage inputs -----------------------------------------------------
        fuselage_tail_angle=35., fuselage_tail_length=5.,
        fuselage_cockpit_length=3., fuselage_cabin_length=30.,
        fuselage_diameter=3.5, fuselage_nose_length=1.,
        # Main wing inputs ----------------------------------------------------
        # Wing positioning
        main_wing_long_pos=0.4, main_wing_trans_pos=0.5, main_wing_lat_pos=0.5,
        # Wing segments inputs
        mw_n_wing_segments=3,
        mw_airfoil_names=['NACA2412', 'NACA2412', 'whitcomb', 'whitcomb'],
        mw_chords=[6., 4.5, 1.2, 0.8], mw_twists=[-2., 0., 3., 5.],
        mw_sweeps_le=[15., 35., 45.], mw_dihedral_angles=[2., 4., 8.],
        mw_spanwise_positions=[0.45, 0.85], mw_span=30., mw_wing_cant=0.,
        # Spars inputs
        mw_n_spars=3,
        mw_spar_chordwise_positions=[[0.2, 0.15, 0.2],
                                     [0.5, 0.55, 0.5],
                                     [0.8, 0.85, 0.8, 0.75]],
        mw_spar_aspect_ratios=[0.2, 0.3, 0.4],
        mw_spar_profiles=['C_', 'I', 'C'],
        mw_spar_spanwise_positions_end=[0.8, 0.7, 0.9],
        # Wing box ribs inputs
        mw_n_ribs_wb=8,
        mw_ribs_wb_spanwise_reference_spars_idx=[0, 0, 0, 0, 1, 1, 1, 1],
        mw_ribs_wb_spanwise_positions=[1e-4, 0.1, 0.2, 0.3,
                                       0.4, 0.6, 0.8, 0.9],
        mw_ribs_wb_orientation_reference_spars=[1, 1, 1, 1, 0, 0, 0, 0],
        mw_ribs_wb_orientation_angles=['flight_direction', 90., 90., 90., 100.,
                                       80., 100., 90.],
        # Trailing edge riblets inputs
        mw_n_ribs_te=8,
        mw_ribs_te_spanwise_reference_spars_idx=[0, 0, 0, 0, 0, 0, 0, 1],
        mw_ribs_te_spanwise_positions=[0.25, 0.1, 0.2, 0.3,
                                       0.45, 0.5, 0.85, 0.9],
        mw_ribs_te_orientation_reference_spars=[1, 1, 1, 1, 0, 0, 0, 0],
        mw_ribs_te_orientation_angles=[90.0, 90.0, 90.0, 90.0, 100.0, 100.0,
                                       100.0, 90.0],
        # Leading edge riblets inputs
        mw_n_ribs_le=8,
        mw_ribs_le_spanwise_reference_spars_idx=[0, 0, 0, 0, 0, 1, 1, 1],
        mw_ribs_le_spanwise_positions=[0.25, 0.1, 0.2, 0.3,
                                       0.4, 0.55, 0.8, 0.9],
        mw_ribs_le_orientation_reference_spars=[1, 2, 2, 1, 0, 0, 0, 0],
        mw_ribs_le_orientation_angles=[90.0, 85.0, 90.0, 90.0, 110.0, 100.0,
                                       100.0, 90.0],
        # Fuel tank inputs
        mw_fuel_tank_boundaries=[0, 3, 5, 7],
        # Movables inputs
        mw_n_movables=2,
        mw_movable_spanwise_starts=[0.1, 0.5],
        mw_movable_spanwise_ends=[0.4, 0.8],
        mw_movable_hingeline_starts=[0.8, 0.85],
        mw_movable_deflections=[5., 10.],
        mw_movables_symmetric=[True, False],
        mw_movables_names=['flap', 'aileron'],
        # Engines inputs
        mw_n_engines=4,
        mw_engine_spanwise_positions=[0.15, 0.5],
        mw_engine_overhangs=[0.4, 0.3],
        mw_engine_thrusts=[50000., 50000.],
        mw_engine_specific_fuel_consumptions=[1.79e-5, 1.79e-5],
        # Horizontal tail inputs ----------------------------------------------
        # Wing positioning
        horizontal_tail_trans_pos=0.4, horizontal_tail_lat_pos=0.5,
        # Wing segments inputs
        ht_n_wing_segments=1,
        ht_airfoil_names=['NACA0018', 'NACA0012'],
        ht_chords=[3., 1.5], ht_twists=[0., 0.],
        ht_sweeps_le=[35.], ht_dihedral_angles=[1.],
        ht_spanwise_positions=[], ht_span=7., ht_wing_cant=0.,
        # Spars inputs
        ht_n_spars=2,
        ht_spar_chordwise_positions=[[0.2, 0.2], [0.8, 0.8]],
        ht_spar_aspect_ratios=[0.4, 0.3],
        ht_spar_profiles=['C_', 'C'],
        ht_spar_spanwise_positions_end=[0.8, 0.8],
        # Wing box ribs inputs
        ht_n_ribs_wb=4,
        ht_ribs_wb_spanwise_reference_spars_idx=[0, 0, 1, 1],
        ht_ribs_wb_spanwise_positions=[1e-3, 0.4, 0.75, 0.95],
        ht_ribs_wb_orientation_reference_spars=[1, 1, 0, 0],
        ht_ribs_wb_orientation_angles=['flight_direction',
                                       'flight_direction',
                                       'flight_direction', 'flight_direction'],
        # Trailing edge riblets inputs
        ht_n_ribs_te=5,
        ht_ribs_te_spanwise_reference_spars_idx=[0, 0, 0, 0, 1],
        ht_ribs_te_spanwise_positions=[0.1, 0.2, 0.4, 0.75, 0.9],
        ht_ribs_te_orientation_reference_spars=[1, 1, 0, 0, 0],
        ht_ribs_te_orientation_angles=['flight_direction',
                                       'flight_direction', 'flight_direction',
                                       'flight_direction', 'flight_direction'],
        # Leading edge riblets inputs
        ht_n_ribs_le=3,
        ht_ribs_le_spanwise_reference_spars_idx=[0, 0, 1],
        ht_ribs_le_spanwise_positions=[0.25, 0.5, 0.9],
        ht_ribs_le_orientation_reference_spars=[0, 0, 0],
        ht_ribs_le_orientation_angles=['flight_direction',
                                       'flight_direction', 'flight_direction'],
        # Fuel tank inputs
        ht_fuel_tank_boundaries=[0, -1],
        # Movables inputs
        ht_n_movables=1,
        ht_movable_spanwise_starts=[0.2],
        ht_movable_spanwise_ends=[0.8],
        ht_movable_hingeline_starts=[0.8],
        ht_movable_deflections=[10.],
        ht_movables_symmetric=[True],
        ht_movables_names=['elevator'],
        # Vertical tail inputs ------------------------------------------------
        # Wing positioning
        vertical_tail_trans_pos=0.5,
        # Wing segments inputs
        vt_n_wing_segments=1,
        vt_airfoil_names=['NACA0018', 'NACA0012'],
        vt_chords=[3., 1.5], vt_twists=[0., 0.],
        vt_sweeps_le=[35.], vt_dihedral_angles=[0.],
        vt_spanwise_positions=[], vt_semi_span=3.5, vt_wing_cant=0.,
        # Spars inputs
        vt_n_spars=2,
        vt_spar_chordwise_positions=[[0.2, 0.2], [0.8, 0.8]],
        vt_spar_aspect_ratios=[0.4, 0.3],
        vt_spar_profiles=['C_', 'C'],
        vt_spar_spanwise_positions_end=[0.8, 0.8],
        # Wing box ribs inputs
        vt_n_ribs_wb=4,
        vt_ribs_wb_spanwise_reference_spars_idx=[0, 0, 1, 1],
        vt_ribs_wb_spanwise_positions=[1e-3, 0.4, 0.75, 0.95],
        vt_ribs_wb_orientation_reference_spars=[1, 1, 0, 0],
        vt_ribs_wb_orientation_angles=['flight_direction',
                                       'flight_direction',
                                       'flight_direction', 'flight_direction'],
        # Trailing edge riblets inputs
        vt_n_ribs_te=5,
        vt_ribs_te_spanwise_reference_spars_idx=[0, 0, 0, 0, 1],
        vt_ribs_te_spanwise_positions=[0.1, 0.2, 0.4, 0.75, 0.9],
        vt_ribs_te_orientation_reference_spars=[1, 1, 0, 0, 0],
        vt_ribs_te_orientation_angles=['flight_direction',
                                       'flight_direction', 'flight_direction',
                                       'flight_direction', 'flight_direction'],
        # Leading edge riblets inputs
        vt_n_ribs_le=3,
        vt_ribs_le_spanwise_reference_spars_idx=[0, 0, 1],
        vt_ribs_le_spanwise_positions=[0.25, 0.5, 0.9],
        vt_ribs_le_orientation_reference_spars=[0, 0, 0],
        vt_ribs_le_orientation_angles=['flight_direction',
                                       'flight_direction', 'flight_direction'],
        # Fuel tank inputs
        vt_fuel_tank_boundaries=[0, -1],
        # Movables inputs
        vt_n_movables=1,
        vt_movable_spanwise_starts=[0.2],
        vt_movable_spanwise_ends=[0.8],
        vt_movable_hingeline_starts=[0.8],
        vt_movable_deflections=[10.],
        vt_movables_symmetric=[True],
        vt_movables_names=['rudder']
    )

    display(obj)
