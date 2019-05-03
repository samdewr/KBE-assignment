from parapy.core import *
from parapy.geom import *
from fuselage_primitives.fuselage import Fuselage
from scissor_plot import ScissorPlot
from wing_primitives.external.wing import Wing
import kbeutils.avl as avl
import math
import numpy as np
from scipy import interpolate

class Aircraft(GeomBase):
    """ This is the class representing the overall aircraft.
    """
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
    mw_ribs_wb_spanwise_reference_spars_idx = Input(validator=val.all_is_number)
    mw_ribs_wb_spanwise_positions = Input(validator=val.all_is_number)
    mw_ribs_wb_orientation_reference_spars = Input(validator=val.all_is_number)
    mw_ribs_wb_orientation_angles = Input()

    mw_n_ribs_te = Input(validator=lambda x: isinstance(x, int))
    mw_ribs_te_spanwise_reference_spars_idx = Input(validator=val.all_is_number)
    mw_ribs_te_spanwise_positions = Input(validator=val.all_is_number)
    mw_ribs_te_orientation_reference_spars = Input(validator=val.all_is_number)
    mw_ribs_te_orientation_angles = Input()

    mw_n_ribs_le = Input(validator=lambda x: isinstance(x, int))
    mw_ribs_le_spanwise_reference_spars_idx = Input(validator=val.all_is_number)
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

    # Engines input
    mw_n_engines = Input(validator=lambda x: isinstance(x, int))
    mw_engine_spanwise_positions = Input()  # validator=val.all_is_number)
    mw_engine_overhangs = Input()  # validator=val.all_is_number)
    mw_engine_diameters_inlet = Input([2., 2.])  # validator=val.all_is_number)
    mw_engine_diameters_outlet = Input([1., 1.])  # validator=val.)
    mw_engine_diameters_part2 = Input([0.5, 0.5])
    mw_engine_length_cones1 = Input([2., 2.])
    mw_engine_length_cones2 = Input([1., 1.])

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

    ht_semi_span = Input(validator=val.is_positive)
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

    # Engines input
    ht_n_engines = Input(0, validator=lambda x: isinstance(x, int))
    ht_engine_spanwise_positions = Input()  # validator=val.all_is_number)
    ht_engine_overhangs = Input()  # validator=val.all_is_number)
    ht_engine_diameters_inlet = Input([2., 2.])  # validator=val.all_is_number)
    ht_engine_diameters_outlet = Input([1., 1.])  # validator=val.)
    ht_engine_diameters_part2 = Input([0.5, 0.5])
    ht_engine_length_cones1 = Input([2., 2.])
    ht_engine_length_cones2 = Input([1., 1.])

<<<<<<< HEAD
    # Horizontal tail Inputs --------------------------------------------------
    vertical_tail_long_pos = Input(validator=val.Between(0, 1))
    vertical_tail_lat_pos = Input(validator=val.Between(0, 1))
=======
    # Vertical tail Inputs --------------------------------------------------
    vertical_tail_trans_pos = Input(validator=val.Range(0, 1))
>>>>>>> 0bf9fa7f1a81ace82a77b933520260cd19b718cb

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

    # Engines input
    vt_n_engines = Input(0, validator=lambda x: isinstance(x, int))
    vt_engine_spanwise_positions = Input()  # validator=val.all_is_number)
    vt_engine_overhangs = Input()  # validator=val.all_is_number)
    vt_engine_diameters_inlet = Input([2., 2.])  # validator=val.all_is_number)
    vt_engine_diameters_outlet = Input([1., 1.])  # validator=val.)
    vt_engine_diameters_part2 = Input([0.5, 0.5])
    vt_engine_length_cones1 = Input([2., 2.])
    vt_engine_length_cones2 = Input([1., 1.])

    __initargs__ = [
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
        'mw_engine_spanwise_positions', 'mw_engine_overhangs'
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
        'vt_engine_spanwise_positions', 'vt_engine_overhangs'
    ]

    # Optional inputs
    name = Input('aircraft')
    color = Input('white')
    transparency = Input(0.5)
    avl_CL_start = Input(0.1)
    avl_CL_end = Input(0.8)
    avl_CL_step = Input(0.1)
    avl_delta_e_start = Input(-30.)
    avl_delta_e_end = Input(31.)
    avl_delta_e_step = Input(30.)

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
                # Engines inputs
                'mw_n_engines->n_engines',
                'mw_engine_spanwise_positions->engine_spanwise_positions',
                'mw_engine_overhangs->engine_overhangs']
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
                # Engines inputs
                'mw_n_engines->n_engines',
                'mw_engine_spanwise_positions->engine_spanwise_positions',
                'mw_engine_overhangs->engine_overhangs'
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
                # Engines inputs
                'vt_n_engines->n_engines',
                'vt_engine_spanwise_positions->engine_spanwise_positions',
                'vt_engine_overhangs->engine_overhangs'
            ]
        )

    @Part
    def horizontal_tail_starboard(self):
        return Wing(
            name='horizontal_tail_starboard',
            location=translate(self.fuselage.point_at_fractions(
                1.,
                self.horizontal_tail_trans_pos,
                self.horizontal_tail_lat_pos),
                'x_', self.ht_chords[0])
            if self.tail_type == 'conventional' else
            self.vertical_tail.sections[-1].position.location,
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
                # Engines inputs
                'ht_n_engines->n_engines',
                'ht_engine_spanwise_positions->engine_spanwise_positions',
                'ht_engine_overhangs->engine_overhangs'
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
                -self.horizontal_tail_lat_pos),
                'x_', self.ht_chords[0])
            if self.tail_type == 'conventional' else
            self.vertical_tail.sections[-1].position.location,
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
                # Engines inputs
                'ht_n_engines->n_engines',
                'ht_engine_spanwise_positions->engine_spanwise_positions',
                'ht_engine_overhangs->engine_overhangs'
            ]
        )

    @Part
    def scissor_plot(self):
        return ScissorPlot(
            # TODO: Als het mogelijk is, deze CL_0 berekeningen enzo even
            #  koppelen aan AVL.
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
                     self.main_wing_starboard.mac_position.x)

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
            mach=0.8,
            reference_area=self.wing_area,
            reference_chord=self.main_wing_starboard.mean_aerodynamic_chord,
            reference_span=self.mw_span,
            reference_point=Point(self.main_wing_starboard.mac_position.x,
                                  0.,
                                  self.main_wing_starboard.mac_position.z)
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
            mach=0.8,
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
                      (mac ** 2 *
                       (self.mw_span + 2.15 * self.fuselage_diameter)) \
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
    def z_h(self):
        return self.horizontal_tail_starboard.position.z - \
               self.main_wing_starboard.position.z

    @Attribute
    def forward_cg(self):
        # TODO Hier nog even de uitgerekende forward and aft c.g's invullen
        return 0.12

    @Attribute
    def aft_cg(self):
        # TODO Hier nog even de uitgerekende forward and aft c.g's invullen
        return 0.3

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
        """

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
        # Stability inputs
        stability_margin=0.05,
        # Fuselage inputs -----------------------------------------------------
        fuselage_tail_angle=30., fuselage_tail_length=5.,
        fuselage_cockpit_length=3., fuselage_cabin_length=20.,
        fuselage_diameter=3., fuselage_nose_length=1.,
        # Tail configuration inputs
        tail_type='conventional',
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
        # Engines inputs
        mw_n_engines=2,
        mw_engine_spanwise_positions=[0.15, 0.5],
        mw_engine_overhangs=[0.4, 0.3],
        # Horizontal tail inputs ----------------------------------------------
        # Wing positioning
        horizontal_tail_trans_pos=0.4, horizontal_tail_lat_pos=0.5,
        # Wing segments inputs
        ht_n_wing_segments=1,
        ht_airfoil_names=['NACA0018', 'NACA0012'],
        ht_chords=[3., 1.5], ht_twists=[0., 0.],
        ht_sweeps_le=[35.], ht_dihedral_angles=[1.],
        ht_spanwise_positions=[], ht_semi_span=3.5, ht_wing_cant=0.,
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
        # Vertical tail inputs ------------------------------------------------
        # Wing positioning
        vertical_tail_trans_pos=0.5,
        # Wing segments inputs
        vt_n_wing_segments=1,
        vt_airfoil_names=['NACA0018', 'NACA0012'],
        vt_chords=[3., 1.5], vt_twists=[0., 0.],
        vt_sweeps_le=[35.], vt_dihedral_angles=[1.],
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
        vt_movables_symmetric=[True]
    )

    display(obj)
