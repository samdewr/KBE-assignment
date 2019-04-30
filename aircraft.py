from parapy.core import *
from parapy.geom import *
from fuselage_primitives.fuselage import Fuselage
from wing_primitives.external.wing import Wing


class Aircraft(GeomBase):
    """ This is the class representing the overall aircraft.
    """
    # Fuselage Inputs ---------------------------------------------------------
    # Wing Inputs
    sweep_angle = Input()
    span = Input()

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
    main_wing_long_pos = Input(validator=val.Between(0, 1))
    main_wing_lat_pos = Input(validator=val.Between(0, 1))

    mw_n_wing_segments = Input(validator=lambda x: isinstance(x, int))

    mw_airfoil_names = Input()
    mw_chords = Input(validator=val.all_is_number)
    mw_twists = Input(validator=val.all_is_number)

    mw_sweeps_le = Input(validator=val.all_is_number)
    mw_dihedral_angles = Input(validator=val.all_is_number)

    mw_spanwise_positions = Input(
        validator=lambda lst: all(0 < x < 1 or x is None for x in lst)
    )

    mw_semi_span = Input(validator=val.is_positive)
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

    # Horizontal tail Inputs --------------------------------------------------
    horizontal_tail_long_pos = Input(validator=val.Between(0, 1))
    horizontal_tail_lat_pos = Input(validator=val.Between(0, 1))

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

    # Horizontal tail Inputs --------------------------------------------------
    vertical_tail_long_pos = Input(validator=val.Between(0, 1))
    vertical_tail_lat_pos = Input(validator=val.Between(0, 1))

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
            location=translate(
                self.fuselage.position.location,
                self.fuselage.position.Vx,
                self.fuselage.length * self.main_wing_long_pos,
                self.fuselage.position.Vy,
                self.fuselage.diameter / 2. * self.main_wing_lat_pos
            ),
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
            location=translate(
                self.fuselage.position.location,
                self.fuselage.position.Vx,
                self.fuselage.length * self.main_wing_long_pos,
                self.fuselage.position.Vy,
                -self.fuselage.diameter / 2. * self.main_wing_lat_pos
            ),
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
            location=translate(
                self.fuselage.end,
                -self.position.Vx,
                self.vt_chords[0]),
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
            location=translate(
                self.fuselage.end, -self.position.Vx, self.ht_chords[0]
            ) if self.tail_type == 'conventional' else
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
            location=translate(
                self.fuselage.end, -self.position.Vx, self.ht_chords[0]
            ) if self.tail_type == 'conventional' else
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

    @Attribute
    def symmetry_plane(self):
        return Plane(self.position, self.position.Vy, self.position.Vx)


    # @Part
    # def scissor_plot(self):
    #     return ScissorPlot(length_fuselage=self.length_fuselage,
    #                        diameter_fuselage=self.diameter_fuselage)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft(
        # Fuselage inputs -----------------------------------------------------
        fuselage_tail_angle=30., fuselage_tail_length=5.,
        fuselage_cockpit_length=3., fuselage_cabin_length=20.,
        fuselage_diameter=3., fuselage_nose_length=1.,
        # Tail configuration inputs
        tail_type='conventional',
        # Main wing inputs ----------------------------------------------------
        # Wing positioning
        main_wing_long_pos=0.4, main_wing_lat_pos=0.5,
        # Wing segments inputs
        mw_n_wing_segments=3,
        mw_airfoil_names=['NACA2412', 'NACA2412', 'whitcomb', 'whitcomb'],
        mw_chords=[6., 4.5, 1.2, 0.8], mw_twists=[-2., 0., 3., 5.],
        mw_sweeps_le=[15., 35., 45.], mw_dihedral_angles=[2., 4., 8.],
        mw_spanwise_positions=[0.45, 0.85], mw_semi_span=15., mw_wing_cant=0.,
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
        horizontal_tail_long_pos=0.4, horizontal_tail_lat_pos=0.5,
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
        vertical_tail_long_pos=0.4, vertical_tail_lat_pos=0.5,
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
