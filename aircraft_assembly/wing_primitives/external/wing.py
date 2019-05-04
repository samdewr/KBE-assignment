from math import radians

import kbeutils.avl as avl
import numpy as np
from parapy.core import *
from parapy.geom import *

from aircraft_assembly.engines.engine import Engine
from aircraft_assembly.wing_primitives.external.airfoil import \
    IntersectedAirfoil
from aircraft_assembly.wing_primitives.external.lifting_surface import \
    LiftingSurface
from aircraft_assembly.wing_primitives.external.movable import Movable
from aircraft_assembly.wing_primitives.fuel.fuel_tank import FuelTank
from aircraft_assembly.wing_primitives.structural_elements.rib import (
    WingBoxRib, TrailingEdgeRiblet, LeadingEdgeRiblet
)
from aircraft_assembly.wing_primitives.structural_elements.spar import \
    FusedSpar


class Wing(SewnShell):
    """ Returns a connected series of lifting surfaces. That is, a wing
    consisting of N wing segments requires:

    Separate lists of length N+1 containing (running from root to tip):
        - Airfoil names
        - Chords
        - Twists

    Separate lists of length N containing (running from root to tip):
        - Leading edge (LE) sweeps
        - Dihedral angles of the segments

    One list of length N-1 containing (running from root to tip):
        - The spanwise position(s) (y/(b/2)) of the intermediate airfoil(s)
          station(s).
          Note that if the wing consists of only one segment/one lifting
          surface, this list has length zero. In this case, no argument
          or an empty list needs to be supplied as input.

    Furthermore, the wing requires as an input:
        - Semi-span

    An optional input is:
        - Wing cant (rotation of the entire wing of a specified angle in
          degrees along a vector along the global 'x' direction)

    """

    # Required inputs
    n_wing_segments = Input(validator=lambda x: isinstance(x, int))

    airfoil_names = Input()
    chords = Input(validator=val.all_is_number)
    twists = Input(validator=val.all_is_number)

    sweeps_le = Input(validator=val.all_is_number)
    dihedral_angles = Input(validator=val.all_is_number)

    spanwise_positions = Input(
        validator=lambda lst: all(0 < x < 1 or x is None for x in lst)
    )

    semi_span = Input(validator=val.is_positive)
    wing_cant = Input(validator=val.is_number)

    # Spar inputs
    n_spars = Input(validator=lambda x: isinstance(x, int))
    spar_chordwise_positions = Input(
        validator=lambda lst: all(isinstance(sublist, list)
                                  for sublist in lst)
    )
    spar_aspect_ratios = Input(validator=val.all_is_number)
    spar_profiles = Input(validator=val.all_is_string)
    spar_spanwise_positions_end = Input(validator=val.all_is_number)

    # Rib inputs
    n_ribs_wb = Input(validator=lambda x: isinstance(x, int))
    ribs_wb_spanwise_reference_spars_idx = Input(validator=val.all_is_number)
    ribs_wb_spanwise_positions = Input(validator=val.all_is_number)
    ribs_wb_orientation_reference_spars = Input(validator=val.all_is_number)
    ribs_wb_orientation_angles = Input()

    n_ribs_te = Input(validator=lambda x: isinstance(x, int))
    ribs_te_spanwise_reference_spars_idx = Input(validator=val.all_is_number)
    ribs_te_spanwise_positions = Input(validator=val.all_is_number)
    ribs_te_orientation_reference_spars = Input(validator=val.all_is_number)
    ribs_te_orientation_angles = Input()

    n_ribs_le = Input(validator=lambda x: isinstance(x, int))
    ribs_le_spanwise_reference_spars_idx = Input(validator=val.all_is_number)
    ribs_le_spanwise_positions = Input(validator=val.all_is_number)
    ribs_le_orientation_reference_spars = Input(validator=val.all_is_number)
    ribs_le_orientation_angles = Input()

    # Fuel tank input
    fuel_tank_boundaries = Input(validator=val.all_is_number)

    # Movable input
    n_movables = Input(validator=lambda x: isinstance(x, int))
    movable_spanwise_starts = Input(validator=val.all_is_number)
    movable_spanwise_ends = Input(validator=val.all_is_number)
    movable_hingeline_starts = Input(validator=val.all_is_number)
    movable_deflections = Input(validator=val.all_is_number)
    movables_symmetric = Input(validator=val.all_is_number)
    movables_names = Input(validator=val.all_is_string)

    # Engines input
    n_engines = Input(validator=lambda x: isinstance(x, int) and x % 2 == 0)
    engine_spanwise_positions = Input(validator=val.all_is_number)
    engine_overhangs = Input(validator=val.all_is_number)
    engine_thrusts = Input(validator=val.all_is_number)
    engine_diameters_inlet = Input([2., 2.], validator=val.all_is_number)
    engine_diameters_outlet = Input([1., 1.], validator=val.all_is_number)
    engine_diameters_part2 = Input([0.5, 0.5], validator=val.all_is_number)
    engine_length_cones1 = Input([2., 2.], validator=val.all_is_number)
    engine_length_cones2 = Input([1., 1.], validator=val.all_is_number)

    tolerance = 1e-7

    __initargs__ = ['n_wing_segments', 'airfoil_names', 'chords', 'twists',
                    'sweeps_le', 'dihedral_angles', 'spanwise_positions',
                    'semi_span', 'wing_cant', 'n_spars',
                    'spar_chordwise_positions', 'spar_aspect_ratios',
                    'spar_profiles', 'spar_spanwise_positions_end',
                    'n_ribs_wb', 'ribs_wb_spanwise_reference_spars_idx',
                    'ribs_wb_spanwise_positions',
                    'ribs_wb_orientation_reference_spars',
                    'ribs_wb_orientation_angles',
                    'n_ribs_te', 'ribs_te_spanwise_reference_spars_idx',
                    'ribs_te_spanwise_positions',
                    'ribs_te_orientation_reference_spars',
                    'ribs_te_orientation_angles',
                    'n_ribs_le', 'ribs_le_spanwise_reference_spars_idx',
                    'ribs_le_spanwise_positions',
                    'ribs_le_orientation_reference_spars',
                    'ribs_le_orientation_angles', 'fuel_tank_boundaries',
                    'n_movables',
                    'movable_spanwise_starts', 'movable_spanwise_ends',
                    'movable_hingeline_starts', 'movable_deflections',
                    'movables_symmetric',
                    'n_engines',
                    'engine_spanwise_positions', 'engine_overhangs',
                    'engine_thrusts', 'engine_diameters_inlet',
                    'engine_diameters_outlet', 'engine_diameters_part2',
                    'engine_length_cones1', 'engine_length_cones2']

    @Input
    def position(self):
        """ Overrides the GeomBase standard position argument, such that
        upon instantiating, the argument "wing_cant" determines the wing's
        orientation.

        :rtype: parapy.geom.generic.positioning.Position
        """
        if self.is_starboard:
            return rotate(Position(self.location),
                          'x', radians(self.wing_cant))
        else:
            return rotate(Position(self.location,
                                   Orientation(x='x', y='y_', z='z')),
                          'x_', radians(self.wing_cant))

    # Optional inputs
    is_starboard = Input(True)
    location = Input(ORIGIN, validator=lambda pt: isinstance(pt, Point))
    airfoil_number_of_points = Input(100, validator=val.is_positive)
    avl_n_chord = Input(6, validator=lambda x: isinstance(x, int))
    avl_n_span = Input(40, validator=lambda x: isinstance(x, int))
    avl_c_spacing = Input(2., validator=val.is_positive)
    avl_s_spacing = Input(1.0, validator=val.is_positive)
    avl_alpha_start = Input(0., validator=val.is_number)
    avl_alpha_end = Input(10., validator=val.is_number)
    avl_alpha_step = Input(0.5, validator=val.is_number)
    transparency = Input(0.8)
    color = Input('white')
    name = Input('wing')

    @Input
    def label(self):
        return self.name

    @Attribute
    def built_from(self):
        # self.check_length()
        return [wing_segment for wing_segment in self.segments]

    @Part
    def spars(self):
        # Q: How do I include a check that gives a warning when ribs and
        #  spars are crossing one another?
        return FusedSpar(
            [self.segments[segment_no]
                 .spars[child.index -
                        sum(segment_no > i
                            for i in self._spar_ends_in_segment[:child.index])]
             for segment_no in range(self._spar_ends_in_segment
                                     [child.index] + 1)],
            quantify=self.n_spars)

    @Part
    def wing_box_ribs(self):
        # Q: How do I ensure that the ribs are placed, such that rib 0 is at
        #  the root, increasing towards the tip.
        return WingBoxRib(
            self,
            map_down=['ribs_wb_spanwise_reference_spars_idx->'
                      'rib_spanwise_reference_spar_idx',
                      'ribs_wb_spanwise_positions->rib_spanwise_position',
                      'ribs_wb_orientation_reference_spars->'
                      'rib_orientation_reference_spar_idx',
                      'ribs_wb_orientation_angles->rib_orientation_angle'],
            quantify=self.n_ribs_wb)

    @Part
    def trailing_edge_riblets(self):
        return TrailingEdgeRiblet(
            self,
            map_down=['ribs_te_spanwise_reference_spars_idx->'
                      'rib_spanwise_reference_spar_idx',
                      'ribs_te_spanwise_positions->rib_spanwise_position',
                      'ribs_te_orientation_reference_spars->'
                      'rib_orientation_reference_spar_idx',
                      'ribs_te_orientation_angles->rib_orientation_angle'],
            quantify=self.n_ribs_te)

    @Part
    def leading_edge_riblets(self):
        return LeadingEdgeRiblet(
            self,
            map_down=['ribs_le_spanwise_reference_spars_idx->'
                      'rib_spanwise_reference_spar_idx',
                      'ribs_le_spanwise_positions->rib_spanwise_position',
                      'ribs_le_orientation_reference_spars->'
                      'rib_orientation_reference_spar_idx',
                      'ribs_le_orientation_angles->rib_orientation_angle'],
            quantify=self.n_ribs_le)

    @Part
    def fuel_tanks(self):
        return FuelTank(self, self.fuel_tank_boundaries[child.index],
                        self.fuel_tank_boundaries[child.index + 1],
                        quantify=len(self.fuel_tank_boundaries) - 1
                        if len(self.fuel_tank_boundaries) != 0 else 0)

    @Part
    def movables(self):
        # Q: cannot subtract movable from wing surface if movable is located
        #  in the second wing segment.
        return Movable(self,
                       map_down=['movable_spanwise_starts->spanwise_start',
                                 'movable_spanwise_ends->spanwise_end',
                                 'movable_hingeline_starts->hingeline_start',
                                 'movable_deflections->deflection',
                                 'movables_symmetric->symmetric',
                                 'movables_names->name'],
                       quantify=self.n_movables)

    @Part
    def engines(self):
        return Engine(position=self.engine_positions[child.index],
                      map_down=['engine_thrusts->thrust',
                                'engine_diameters_inlet->diameter_inlet',
                                'engine_diameters_outlet->diameter_outlet',
                                'engine_diameters_part2->diameter_part2',
                                'engine_length_cones1->length_cone1',
                                'engine_length_cones2->length_cone2'],
                      quantify=int(self.n_engines / 2))

    @Part(in_tree=False)
    def segments(self):
        """ Return the wing segments that make up the entire wing. This part
        is not shown in the object tree. However, it is used in generating
        the overall wing surface and the contained spars.

        :rtype: list[lifting_surface.LiftingSurface]
        """
        return LiftingSurface(
            quantify=self.n_wing_segments,
            map_down=['_segment_spans->segment_span', 'sweeps_le->sweep_le',
                      'dihedral_angles->dihedral', '_twists_root->twist_root',
                      '_twists_tip->twist_tip', '_chords_root->chord_root',
                      '_chords_tip->chord_tip',
                      '_airfoil_names_root->airfoil_name_root',
                      '_airfoil_names_tip->airfoil_name_tip',
                      '_segment_n_spars->n_spars',
                      '_spar_chordwise_positions_root->'
                      'spar_chordwise_positions_root',
                      '_spar_chordwise_positions_tip->'
                      'spar_chordwise_positions_tip',
                      '_spar_aspect_ratios->spar_aspect_ratios',
                      '_spar_profiles->spar_profiles',
                      '_spar_spanwise_positions_end->'
                      'spar_spanwise_positions_end'
                      ],
            position=self.position if child.index == 0 else
            Position(child.previous.tip_airfoil.location,
                     child.previous.orientation),
            transparency=0.8,
            name='wing_segment' + str(child.index)
        )

    # Wing specific attributes
    @Attribute
    def trailing_edge(self):
        """ Builds one continuous trailing edge wire out of the individual
        trailing edges of the distinct wing segments.

        :rtype: parapy.geom.occ.wire.Wire
        """
        return Wire([segment.trailing_edge for segment in self.segments])

    @Attribute
    def leading_edge(self):
        """ Builds one continuous trailing edge wire out of the individual
        trailing edges of the distinct wing segments.

        :rtype: parapy.geom.occ.wire.Wire
        """
        return Wire([segment.leading_edge for segment in self.segments])

    @Attribute
    def lower_surface(self):
        """ Returns the lower surface of the entire wing as a SewnShell of
        the different wing segments.

        :rtype: parapy.geom.occ.sewing.SewnShell
        """
        return SewnShell([wing_segment.lower_surface
                          for wing_segment in self.segments])

    @Attribute
    def upper_surface(self):
        """ Returns the upper surface of the entire wing as a SewnShell of
        the different wing segments.

        :rtype: parapy.geom.occ.sewing.SewnShell
        """
        return SewnShell([wing_segment.upper_surface
                          for wing_segment in self.segments])

    @Attribute
    def plane(self):
        """ Returns an infinite Plane instance that runs span-wise and in
        the flow direction, through the wing's root airfoil's nose.

        :rtype: parapy.geom.occ.surface.Plane
        """
        return Plane(self.position, self.position.Vz, self.position.Vy)

    @Attribute(settable=False)
    def planform(self):
        """ Returns the planform of this overall wing by making a Compound
        out of the children segments' planforms.

        :rtype: parapy.geom.occ.compound.Compound
        """
        return Compound([segment.planform for segment in self.segments])

    @Attribute(settable=False)
    def reference_area(self):
        return sum(segment.planform.area for segment in self.segments)

    @Attribute(settable=False)
    def taper_ratio(self):
        return self.sections[-1].chord / self.sections[0].chord

    @Attribute(settable=False)
    def mean_aerodynamic_chord(self):
        """ Returns the mean aerodynamic chord (length) of this overall wing.

        :rtype: float
        """
        return sum(segment.mean_aerodynamic_chord * segment.reference_area
                   for segment in self.segments) / self.reference_area

    @Attribute(settable=False)
    def sweep_c_over_4(self):
        """ Return the weighted quarter-chord sweep of this wing.

        :rtype: float
        """
        return sum(segment.sweep_c_over_4 * segment.segment_span
                   for segment in self.segments) / self.semi_span

    @Attribute(settable=False)
    def x_lemac(self):
        """ Returns the x-coordinate of the leading edge of the mean
        aerodynamic chord.

        :rtype: float
        """
        return sum(segment.x_lemac * segment.reference_area
                   for segment in self.segments) / self.reference_area

    @Attribute(settable=False)
    def mac_position(self):
        """ Returns the quarter-chord position of the mean aerodynamic chord of
        this overall wing.

        :rtype: parapy.geom.generic.positioning.Position
        """
        y_mac = sum(segment.mac_position.y * segment.reference_area
                    for segment in self.segments) / self.reference_area
        x_mac = self.x_lemac + self.mean_aerodynamic_chord / 4.
        return Point(x_mac, y_mac, self.position.z)

    @Attribute
    def closed_solid(self):
        """ Return a solid version of this wing (thus without
        structural elements) with closed root and tip airfoils.

        :rtype: parapy.geom.occ.sewing.CloseSurface
        """
        return CloseSurface([wing_segment for wing_segment in self.segments])

    @Attribute(in_tree=True)
    def movable_sections(self):
        """ Returns airfoil sections at the boundaries of the control surface
        present on this wing. These are necessary because an AVL control
        surface runs over the entire trailing edge of the surface between
        two sections.

        :rtype: list[wing_primitives.airfoil.IntersectedAirfoil]
        """
        controls = [avl.Control(
            name=self.movables_names[idx],
            gain=-1 if (not self.movables_symmetric[idx] and
                        self.is_starboard) else 1,
            x_hinge=self.movable_hingeline_starts[idx],
            duplicate_sign=1 if self.movables_symmetric[idx] else -1
        )
            for idx in range(len(self.movables))]

        return [IntersectedAirfoil(self, pln, controls=controls[idx])
                for idx, movable in enumerate(self.movables)
                for pln in movable.spanwise_planes]

    @Attribute
    def sections(self):
        """ Return the airfoil sections of this wing at the defined stations.

        :rtype: list[wing_primitives.airfoil.Airfoil]
        """
        return [self.segments[0].root_airfoil] + [segment.tip_airfoil for
                                                  segment in self.segments]

    @Attribute
    def closed_shell(self):
        """ Return an outer shell version of this wing (thus without
        structural elements) with closed root and tip airfoils.

        :rtype: parapy.geom.occ.shell.Shell_
        """
        return self.closed_solid.shells[0]

    # AVL analysis attributes and parts

    @Part
    def avl_analysis(self):
        """ The AVL analysis wrapper part.
        """
        return avl.Interface(cases=self.cases,
                             configuration=self.avl_configuration)

    @Attribute
    def avl_surface(self):
        """ Return the AVL Surface geometry. This representation is required
        the AVL wrapper.

        :rtype: parapy.lib.avl.primitives.Surface
        """
        sections = sorted(self.sections + self.movable_sections,
                          key=lambda s: s.position.y)
        avl_sections = [section.avl_section for section in sections]

        return avl.Surface(name=self.name,
                           sections=avl_sections,
                           n_chordwise=self.avl_n_chord,
                           n_spanwise=self.avl_n_span,
                           chord_spacing=self.avl_c_spacing,
                           span_spacing=self.avl_s_spacing,
                           y_duplicate=0.0 if self.wing_cant != 90. else None)

    @Attribute
    def avl_configuration(self):
        """ The 'configuration' of this wing, such that it can be
        interpreted by AVL.

        .. note::
           The analysis run in AVL is *not* for a semi-wing. It is assumed
           that analyses are always run for symmetric wings, because the
           obtained values would not make sense otherwise.
        """
        is_root = self.parent is None
        mac = self.mean_aerodynamic_chord if is_root \
            else self.parent.mean_aerodynamic_chord
        span = self.semi_span * 2 if is_root else self.parent.mw_span
        ref_point = Point(self.mac_position.x, 0., self.mac_position.y) if \
            is_root else self.parent.mac_position
        return avl.Configuration(name=self.name,
                                 surfaces=[self.avl_surface],
                                 mach=self.parent.mach,
                                 # TODO check whether reference area and
                                 #  chord are still correct for horizontal
                                 #  and vertical tails.
                                 reference_area=self.reference_area * 2.,
                                 reference_chord=mac,
                                 reference_span=span,
                                 reference_point=ref_point)

    @Attribute
    def cases(self):
        """ The run cases of AVL.
        .. note::
           The ailerons are never deflected, because due to the perfect
           symmetry, the CL does not change as a result
        """
        return [avl.Case(
            name='alpha_{0:0.1f}'.format(alpha),
            settings={'alpha': avl.Parameter(name='alpha',
                                             value=alpha)})
                for alpha in np.arange(self.avl_alpha_start,
                                       self.avl_alpha_end,
                                       self.avl_alpha_step)]

    @Attribute
    def CL_0(self):
        """ Return the zero-angle-of-attack lift coefficient of this wing.

        :rtype: float
        """
        alphas = np.arange(self.avl_alpha_start, self.avl_alpha_end,
                           self.avl_alpha_step)
        CLs = [self.get_CL(alpha) for alpha in alphas]
        return np.polyfit(alphas, CLs, 1)[-1]

    @Attribute
    def CD_0(self):
        """ Return the zero-angle-of-attack lift coefficient of this wing.

        :rtype: float
        """
        alphas = np.arange(self.avl_alpha_start, self.avl_alpha_end,
                           self.avl_alpha_step)
        CDs = [self.get_CD(alpha) for alpha in alphas]
        return np.polyfit(alphas, CDs, 1)[-1]

    @Attribute
    def Cm_0(self):
        """ Return the zero-angle-of-attack pitching moment coefficient of
        this wing around its aerodynamic centre.

        :rtype: float
        """
        return self.get_Cm(alpha=0.)

    @Attribute
    def CL_alpha(self):
        """ Return the lift curve slope of this wing in deg\ :sup:`-1`\ .

        :rtype: float
        """
        alphas = np.arange(self.avl_alpha_start, self.avl_alpha_end,
                           self.avl_alpha_step)
        CLs = [self.get_CL(alpha) for alpha in alphas]
        return np.polyfit(alphas, CLs, 1)[0]

    def get_CL(self, alpha):
        """ Return the lift coefficient for a given alpha (angle of attack).

        :param alpha: angle of attack in degrees
        :type alpha: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: float
        """
        return self.get_quantity('CLtot', alpha)

    def get_Cm(self, alpha):
        """ Return the pitching moment coefficient for a given alpha (angle of
        attack).

        :param alpha: angle of attack in degrees
        :type alpha: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: float
        """
        return self.get_quantity('Cmtot', alpha)

    def get_CD(self, alpha):
        """ Return the pitching moment coefficient for a given alpha (angle of
        attack).

        :param alpha: angle of attack in degrees
        :type alpha: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: float
        """
        return self.get_quantity('CDtot', alpha)

    def get_quantity(self, quantity, alpha):
        """ Return the drag coefficient for a given alpha (angle of attack).

        :param quantity: the quantity that is requested
        :type quantity: str

        :param alpha: angle of attack in degrees
        :type alpha: float | int

        :raises Exception: if alpha is out of the range of analysed alphas.

        :rtype: float
        """
        if not self.avl_alpha_start <= alpha <= self.avl_alpha_end:
            raise Exception(
                'The requested {} for alpha: {} is out of the range of '
                'alpha_start: {} and alpha_end: {}. '
                'Extrapolation is not supported.'
                .format(quantity, alpha,
                        self.avl_alpha_start, self.avl_alpha_end)
            )

        alphas = np.arange(self.avl_alpha_start, self.avl_alpha_end,
                           self.avl_alpha_step)
        values = [self.avl_analysis.results
                  ['alpha_{0:0.1f}'.format(float(_alpha))]['Totals'][quantity]
                  for _alpha in alphas]

        return np.interp(alpha, alphas, values)

    def get_custom_avl_results(self, alpha, show_trefftz_plot=False,
                               show_geometry=False, **kwargs):
        """

        :param alpha: the angle of attack of the wing.
        :type alpha: float
        :param show_trefftz_plot: show the trefftz plot?
        :type show_trefftz_plot: bool
        :param show_geometry: show the wing geometry?
        :type show_geometry: bool
        :param kwargs: a (set of) key-value pair(s) defining a (set of)
            movable deflection(s).

        """
        CASE_PARAMETERS = {'alpha': 'alpha', 'beta': 'beta',
                           'roll_rate': 'pb/2V', 'pitch_rate': 'qc/2V',
                           'yaw_rate': 'rb/2V'}

        VALID_CONSTRAINTS = ['alpha', 'beta', 'pb/2V', 'qc/2V',
                             'rb/2V', 'CL', 'CY', 'Cl', 'Cm', 'Cn']

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

    # Attributes helping in instantiating LiftingSurface child objects
    @Attribute(settable=False)
    def _segment_spans(self):
        """ Attribute that is used to map_down attributes to wing children
        (wing segments). Each element in the list that is returned represents
        the span of each wing segment with the child index corresponding to
        the list index.

        :rtype: list[float]
        """
        stations = [0.] + self.spanwise_positions + [1.]
        return [self.semi_span * (y2 - y1)
                for y1, y2 in zip(stations[:-1], stations[1:])]

    @Attribute(settable=False)
    def _twists_root(self):
        """ Attribute that is used to map_down attributes to wing children
        (wing segments). Each element in the list that is returned represents
        the twist at the root of the wing segment with the child
        index corresponding to the list index.

        :rtype: list[float]
        """
        return self.twists[:-1]

    @Attribute(settable=False)
    def _twists_tip(self):
        """ Attribute that is used to map_down attributes to wing children
        (wing segments). Each element in the list that is returned represents
        the twist at the tip of the wing segment with the child
        index corresponding to the list index.

        :rtype: list[float]
        """
        return self.twists[1:]

    @Attribute(settable=False)
    def _chords_root(self):
        """ Attribute that is used to map_down attributes to wing children
        (wing segments). Each element in the list that is returned represents
        the chord at the root of the wing segment with the child
        index corresponding to the list index.

        :rtype: list[float]
        """
        return self.chords[:-1]

    @Attribute(settable=False)
    def _chords_tip(self):
        """ Attribute that is used to map_down attributes to wing children
        (wing segments). Each element in the list that is returned represents
        the chord at the tip of the wing segment with the child
        index corresponding to the list index.

        :rtype: list[float]
        """
        return self.chords[1:]

    @Attribute(settable=False)
    def _airfoil_names_root(self):
        """ Attribute that is used to map_down attributes to wing children
        (wing segments). Each element in the list that is returned represents
        the airfoil name at the root of the wing segment with the child
        index corresponding to the list index.

        :rtype: list[str]
        """
        return self.airfoil_names[:-1]

    @Attribute(settable=False)
    def _airfoil_names_tip(self):
        """ Attribute that is used to map_down attributes to wing children
        (wing segments). Each element in the list that is returned represents
        the airfoil name at the tip of the wing segment with the child
        index corresponding to the list index.

        :rtype: list[str]
        """
        return self.airfoil_names[1:]

    # Attributes helping in instantiating Spar child objects
    @Attribute(settable=False)
    def _spar_ends_in_segment(self):
        """ Returns a list of indices in which wing segment the
        corresponding spars end.

        :rtype: list[int]
        """

        spar_spans = [self.semi_span * spar_frac
                      for spar_frac in self.spar_spanwise_positions_end]
        ending_segment = []
        for spar_span in spar_spans:
            for segment_idx, segment_span in enumerate(self._segment_spans):
                spar_span -= segment_span
                if spar_span <= self.tolerance:
                    ending_segment.append(segment_idx)
                    break
        return ending_segment

    @Attribute(settable=False)
    def _segment_n_spars(self):
        """ Returns the number of spars that is contained within each wing
        segment.

        :rtype: list[int]
        """
        n_spars_left = self.n_spars
        n_spars_in_segment = [self.n_spars]
        for segment_no in range(self.n_wing_segments - 1):
            n_spars_left -= self._spar_ends_in_segment.count(segment_no)
            n_spars_in_segment += [n_spars_left]
        return n_spars_in_segment

    @Attribute(settable=False)
    def _spar_chordwise_positions_root(self):
        """ Returns the chordwise positions at the root of the wing
        segment of the spar. The output is a list of lists containing
        floats. The first level of list indices corresponds to the wing
        segment (child) index. The second level corresponds to each spanwise
        station.

        :rtype: list[list[float]]
        """
        running_spar_indices = set(range(self.n_spars))

        segment_root_positions = []
        for segment_no in range(self.n_wing_segments):

            segment_root_positions.append(
                [self.spar_chordwise_positions[i][segment_no]
                 for i in running_spar_indices]
            )

            spars_idx_ending_here = {
                i for i, x in enumerate(self._spar_ends_in_segment)
                if x == segment_no
            }

            running_spar_indices -= spars_idx_ending_here
        return segment_root_positions

    @Attribute(settable=False)
    def _spar_chordwise_positions_tip(self):
        """ Returns the chordwise positions at the tip of the wing
        segment of the spar. The output is a list of lists containing
        floats. The first level of list indices corresponds to the wing
        segment (child) index. The second level corresponds to each spanwise
        station.

        :rtype: list[list[float]]
        """
        running_spar_indices = set(range(self.n_spars))
        segment_root_positions = []

        for segment_no in range(self.n_wing_segments):

            segment_root_positions.append(
                [self.spar_chordwise_positions[i][segment_no + 1]
                 for i in running_spar_indices]
            )

            running_spar_indices -= {
                i for i, x in enumerate(self._spar_ends_in_segment)
                if x == segment_no
            }
        return segment_root_positions

    @Attribute
    def _spar_aspect_ratios(self):
        """ Attribute that helps in mapping down the spar aspect ratios to
        the lower-level wing segments

        :rtype: list[list[float]]
        """
        running_spar_indices = set(range(self.n_spars))
        segment_aspect_ratios = []

        for segment_no in range(self.n_wing_segments):
            segment_aspect_ratios.append(
                [self.spar_aspect_ratios[i] for i in running_spar_indices]
            )

            running_spar_indices -= {
                i for i, x in enumerate(self._spar_ends_in_segment)
                if x == segment_no
            }
        return segment_aspect_ratios

    @Attribute
    def _spar_profiles(self):
        """ Attribute that helps in mapping down the spar profiles to the
        lower-level wing segments

        :rtype: list[list[str]]
        """
        running_spar_indices = set(range(self.n_spars))
        segment_profiles = []

        for segment_no in range(self.n_wing_segments):
            segment_profiles.append(
                [self.spar_profiles[i] for i in running_spar_indices]
            )

            running_spar_indices -= {
                i for i, x in enumerate(self._spar_ends_in_segment)
                if x == segment_no
            }
        return segment_profiles

    @Attribute
    def _spar_spanwise_positions_end(self):
        """ Attribute that helps in mapping down the spar spanwise lengths to
        the lower-level wing segments

        :rtype: list[list[float]]
        """
        spar_lengths = [self.semi_span * pos
                        for pos in self.spar_spanwise_positions_end]
        spar_length_relative_to_segment = []

        for spar_idx, spar_length in enumerate(spar_lengths):
            spar_length_relative_to_segment.append([])
            for segment_span in self._segment_spans:
                if spar_length > segment_span + self.tolerance:
                    spar_length_relative_to_segment[spar_idx].append(1.)
                    spar_length -= segment_span
                else:
                    spar_length_relative_to_segment[spar_idx].append(
                        spar_length / segment_span)
                    break
        # Transpose the matrix containing the proper fractions in the end.
        return [[row[segment_no]
                 for row in spar_length_relative_to_segment
                 if segment_no < len(row)]
                for segment_no in range(self.n_wing_segments)]

    # Attributes for the engine parts
    @Attribute
    def engine_positions(self):
        """ Determines the positions of the :any:`engines`, based on the
        specified overhang of the engine, spanwise position, and moving it
        downward by half the engine inlet radius.

        :rtype: list[parapy.geom.generic.positioning.Point]
        """
        planes = [Plane(translate(self.position, self.position.Vy,
                                  spanwise * self.semi_span),
                        self.position.Vy, self.position.Vx)
                  for spanwise in self.engine_spanwise_positions]

        points_le = [self.leading_edge.intersection_point(pln)
                     for pln in planes]

        engine_lengths = [length1 + length2 for length1, length2 in
                          zip(self.engine_length_cones1,
                              self.engine_length_cones2)]

        forward_points = [
            translate(point, self.position.Vx_, length * (1. - overhang))
            for point, length, overhang in
            zip(points_le, engine_lengths, self.engine_overhangs)
                          ]

        engine_positions = [translate(point, self.position.Vz_, diameter / 1.5)
                            for point, diameter in
                            zip(forward_points, self.engine_diameters_inlet)]

        return [Position(pnt) for pnt in engine_positions]

    # Validator function for input lengths of lists for generation of
    # LiftingSurface child objects.
    def check_length(self):
            """ Checks if the input lists have the required lengths upon
            instantiating the geometry.

            :raises ValueError:
                If the input lengths are not correct.
            """
            if (len(self.airfoil_names) == len(self.chords) == len(self.twists)
                    == len(self.sweeps_le) + 1 == len(self.dihedral_angles) + 1
                    == len(self.spanwise_positions) + 2
                    == self.n_wing_segments + 1):
                pass
            else:
                raise ValueError('The length of the input lists is not correct'
                                 '. Please check the documentation of the Wing'
                                 ' class to see the required lengths.')


if __name__ == '__main__':
    from parapy.gui import display
    obj = Wing(
        # Wing segments inputs
        n_wing_segments=3,
        airfoil_names=['NACA2412', 'NACA2412', 'NACA23012', 'NACA23012'],
        chords=[6., 4.5, 1.2, 0.8], twists=[0., 0., 3., 5.],
        sweeps_le=[15., 35., 45.], dihedral_angles=[2., 4., 8.],
        spanwise_positions=[0.45, 0.85], semi_span=15., wing_cant=0.,
        # Spars inputs
        n_spars=3,
        spar_chordwise_positions=[[0.2, 0.15, 0.2],
                                  [0.5, 0.55, 0.5],
                                  [0.8, 0.85, 0.8, 0.75]],
        spar_aspect_ratios=[0.2, 0.3, 0.4], spar_profiles=['C_', 'I', 'C'],
        spar_spanwise_positions_end=[0.8, 0.7, 0.9],
        # Wing box ribs inputs
        n_ribs_wb=8,
        ribs_wb_spanwise_reference_spars_idx=[0, 0, 0, 0, 1, 1, 1, 1],
        ribs_wb_spanwise_positions=[1e-4, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 0.9],
        ribs_wb_orientation_reference_spars=[1, 1, 1, 1, 0, 0, 0, 0],
        ribs_wb_orientation_angles=['flight_direction', 90., 90., 90., 100.,
                                    80., 100., 90.],
        # Trailing edge riblets inputs
        n_ribs_te=8,
        ribs_te_spanwise_reference_spars_idx=[0, 0, 0, 0, 0, 0, 0, 1],
        ribs_te_spanwise_positions=[0.25, 0.1, 0.2, 0.3, 0.45, 0.5, 0.85, 0.9],
        ribs_te_orientation_reference_spars=[1, 1, 1, 1, 0, 0, 0, 0],
        ribs_te_orientation_angles=[90.0, 90.0, 90.0, 90.0, 100.0, 100.0,
                                    100.0, 90.0],
        # Leading edge riblets inputs
        n_ribs_le=8,
        ribs_le_spanwise_reference_spars_idx=[0, 0, 0, 0, 0, 1, 1, 1],
        ribs_le_spanwise_positions=[0.25, 0.1, 0.2, 0.3, 0.4, 0.55, 0.8, 0.9],
        ribs_le_orientation_reference_spars=[1, 2, 2, 1, 0, 0, 0, 0],
        ribs_le_orientation_angles=[90.0, 85.0, 90.0, 90.0, 110.0, 100.0,
                                    100.0, 90.0],
        # Fuel tank inputs
        fuel_tank_boundaries=[0, 3, 5, 7],
        # Movables inputs
        n_movables=2,
        movable_spanwise_starts=[0.1, 0.5], movable_spanwise_ends=[0.4, 0.8],
        movable_hingeline_starts=[0.8, 0.85], movable_deflections=[5., 10.],
        movables_symmetric=[True, False], movables_names=['flap', 'aileron'],
        # Engines inputs
        n_engines=2,
        engine_spanwise_positions=[0.15, 0.5], engine_overhangs=[0.4, 0.3])
    obj2 = Wing(2, ['NACA2412', 'NACA2412', 'whitcomb'],
                [6., 4.5, 1.2], [-2., 0., 3.], [15., 35.],
                [2., 4.], [0.45], 15., 0., 2,
                [[0.2, 0.15, 0.2],
                 [0.5, 0.55, 0.5],
                 [0.8, 0.85, 0.8, 0.75]], [0.2, 0.3, 0.4], ['C_', 'I', 'C'],
                [0.8, 0.7, 0.9],
                8, [0, 0, 0, 0, 1, 1, 1, 1],
                [1e-4, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 0.9],
                [1, 1, 1, 1, 0, 0, 0, 0],
                ['flight_direction', 90., 90., 90., 100., 80., 100., 90.],
                8, [0, 0, 0, 0, 0, 0, 0, 1],
                [0.25, 0.1, 0.2, 0.3, 0.45, 0.5, 0.85, 0.9],
                [1, 1, 1, 1, 0, 0, 0, 0],
                [90.0, 90.0, 90.0, 90.0, 100.0, 100.0, 100.0, 90.0],
                8, [0, 0, 0, 0, 0, 1, 1, 1],
                [0.25, 0.1, 0.2, 0.3, 0.4, 0.55, 0.8, 0.9],
                [1, 1, 1, 1, 0, 0, 0, 0],
                [90.0, 85.0, 90.0, 90.0, 110.0, 100.0, 100.0, 90.0],
                [0, 3, 5, 7],
                2,
                [0.1], [0.4], [0.8], [10.])

    display(obj)
