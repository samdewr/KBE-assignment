import math
from math import tan, radians, degrees

import kbeutils.avl as avl
from parapy.core import *
from parapy.geom import *

from classes.wing_primitives.external.airfoil import Airfoil
from classes.wing_primitives.structural_elements.spar import \
    SparSegment


class LiftingSurface(LoftedSurface):
    """ The class that represents a lifting surface, which has a:
            - Root airfoil
            - Root chord
            - Root twist
            - Tip airfoil
            - Tip chord
            - Tip twist
            - Segment semi_span
            - Leading edge (LE) sweep angle
            - Dihedral angle
    """

    __initargs__ = ['airfoil_name_root', 'chord_root', 'twist_root',
                    'airfoil_name_tip', 'chord_tip', 'twist_tip',
                    'segment_span', 'sweep_le', 'dihedral',
                    'n_spars', 'spar_chordwise_positions_root',
                    'spar_chordwise_positions_tip', 'spar_aspect_ratios',
                    'spar_spanwise_positions_end']

    # Required inputs
    airfoil_name_root = Input(validator=val.is_string)
    chord_root = Input(validator=val.is_positive)
    twist_root = Input(validator=val.is_number)

    airfoil_name_tip = Input(validator=val.is_string)
    chord_tip = Input(validator=val.is_positive)
    twist_tip = Input(validator=val.is_number)

    segment_span = Input(validator=val.is_positive)
    sweep_le = Input(validator=val.is_number)
    dihedral = Input(validator=val.is_number)

    # Spar related inputs
    n_spars = Input(validator=lambda x: isinstance(x, int))
    spar_chordwise_positions_root = Input(validator=val.all_is_number)
    spar_chordwise_positions_tip = Input(validator=val.all_is_number)
    spar_aspect_ratios = Input(validator=val.all_is_number)
    spar_profiles = Input(validator=val.all_is_string)
    spar_spanwise_positions_end = Input(validator=val.all_is_number)

    # Optional inputs
    # Q: Should I include all "low-level" optional inputs, such that they can
    #   be changed at the "higher" levels?
    airfoil_number_of_points = Input(100)
    name = Input('lifting_surface')

    avl_n_chord = Input(6)
    avl_n_span = Input(20)
    avl_c_spacing = Input(2.)
    avl_s_spacing = Input(1.0)

    @Input
    def label(self):
        return self.name

    # Inputs for the LoftedSurface class
    @Attribute
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]

    # Generate and position root airfoil
    @Attribute
    def root_airfoil(self):
        """ The fitted curve through the root airfoil coordinate points,
        scaled with the airfoil's chord length.

        :return: the fitted curve through the airfoil coordinates.
        :rtype: airfoil.Airfoil
        """
        return Airfoil(
            self.airfoil_name_root, self.chord_root, self.twist_root,
            position=rotate(self.position,
                            'y' if self.parent.is_starboard else 'y_',
                            radians(self.twist_root)),
            name='root_airfoil')

    # Tip airfoil loading and scaling
    @Attribute
    def tip_airfoil(self):
        """ The fitted curve through the tip airfoil coordinate points,
        scaled with the airfoil's chord length.

        :return: the fitted curve through the airfoil coordinates.
        :rtype: airfoil.Airfoil
        """
        return Airfoil(
            self.airfoil_name_tip, self.chord_tip, self.twist_tip,
            position=rotate(
                translate(
                    self.position,
                    'y', self.segment_span,
                    'x', self.segment_span * tan(radians(self.sweep_le)),
                    'z', self.segment_span * tan(radians(self.dihedral))),
                'y' if self.parent.is_starboard else 'y_',
                radians(self.twist_tip)),
            name='tip_airfoil'
        )

    @Attribute
    def trailing_edge(self):
        """ Returns the trailing edge of this lifting surface segment by
        making a line segment of the trailing edge points of the inboard and
        outboard airfoils. Orientation is semi_span-wise outward.

        :rtype: parapy.geom.occ.curve.LineSegment
        """
        return LineSegment(self.root_airfoil.trailing_edge_point,
                           self.tip_airfoil.trailing_edge_point)

    @Attribute
    def leading_edge(self):
        """ Returns the leading edge of this lifting surface segment by
        making a line segment of the leading edge points of the inboard and
        outboard airfoils. Orientation is semi_span-wise outward.

        :rtype: parapy.geom.occ.curve.LineSegment
        """
        return LineSegment(self.root_airfoil.leading_edge_point,
                           self.tip_airfoil.leading_edge_point)

    @Attribute
    def upper_surface(self):
        """ Return the upper surface of the wing segment,
        by lofting the root and tip airfoils upper halves..

        :rtype: parapy.geom.occ.face.Face_
        """
        return LoftedSurface([self.root_airfoil.upper_half,
                              self.tip_airfoil.upper_half])

    @Attribute
    def lower_surface(self):
        """ Return the lower surface of the wing segment,
        by lofting the root and tip airfoil upper halves.

        :rtype: parapy.geom.occ.face.Face_
        """
        return LoftedSurface([self.root_airfoil.lower_half,
                              self.tip_airfoil.lower_half])

    @Attribute(settable=False)
    def taper_ratio(self):
        return self.chord_tip / self.chord_root

    @Attribute(settable=False)
    def mean_aerodynamic_chord(self):
        """ Returns the mean aerodynamic chord of this wing segment.

        :rtype: float
        """
        return 2. / 3. * self.chord_root * ((1. + self.taper_ratio +
                                             self.taper_ratio ** 2.) /
                                            (1. + self.taper_ratio))

    @Attribute
    def x_lemac(self):
        """ Returns the x coordinate of the leading edge of the mean
        aerodynamic chord of this wing segment.

        :rtype: float
        """
        x_r, y_r, z_r = self.root_airfoil.position
        x_t, y_t, z_t = self.tip_airfoil.position
        return x_r + (x_t - x_r) * ((1. + 2. * self.taper_ratio) /
                                    (3. + 3. * self.taper_ratio))

    @Attribute(settable=False)
    def mac_position(self):
        """ Returns the quarter-chord position of the mean aerodynamic chord of
        this wing segment.

        :rtype: parapy.geom.generic.positioning.Position
        """
        x_r, y_r, z_r = self.root_airfoil.position
        x_t, y_t, z_t = self.tip_airfoil.position
        x_mac = self.x_lemac + self.mean_aerodynamic_chord / 4
        y_mac = y_r + (y_t - y_r) * ((1. + 2. * self.taper_ratio) /
                                     (3. + 3. * self.taper_ratio))
        return Point(x_mac, y_mac, z_r)

    @Attribute(settable=False)
    def plane(self):
        """ Returns an infinite Plane instance that runs span-wise and in
        the flow direction, through the wing's root airfoil's nose.

        :rtype: parapy.geom.occ.surface.Plane
        """
        return Plane(self.position, self.position.Vz, self.position.Vy)

    @Attribute(settable=False)
    def planform(self):
        """ Returns a surface that represents the planform of the wing
        segment by projecting the tip and root chord lines and the leading
        and trailing edges on self.plane in the negative z direction.

        :rtype: parapy.geom.occ.surface.FilledSurface
        """
        curves = [self.leading_edge, self.tip_airfoil.chord_line,
                  self.trailing_edge, self.root_airfoil.chord_line]
        projected_crvs = [ProjectedCurve(crv, self.plane, self.orientation.z_)
                          for crv in curves]
        return FilledSurface(projected_crvs)

    @Attribute(settable=False)
    def reference_area(self):
        return self.planform.area

    @Attribute
    def sweep_c_over_4(self):
        """ Return the quarter-chord sweep of this wing segment.

        :rtype: float
        """
        return math.degrees(
            math.atan(math.tan(math.radians(self.sweep_le)) +
                      self.root_airfoil.chord / (2. * self.segment_span) *
                      (self.taper_ratio - 1.))
        )

    # Spars definition
    @Part
    def spars(self):
        """ Return a quantified Spar object, running in spanwise direction.
        Note that each spar is defined with respect to the wing segment it
        is in; that means the spars running throughout the wing but through
        different segments are considered separate spars, though they are
        connected.

        :rtype: spar.Spar
        """
        return SparSegment(
            self,
            quantify=self.n_spars,
            map_down=['spar_chordwise_positions_root->chordwise_pos_root',
                      'spar_chordwise_positions_tip->chordwise_pos_tip',
                      'spar_aspect_ratios->aspect_ratio',
                      'spar_profiles->profile',
                      'spar_spanwise_positions_end->spanwise_pos_end'],
            position=translate(self.position,
                               self.root_airfoil.chord_line.direction_vector,
                               self.root_airfoil.chord_line.length *
                               self.spar_chordwise_positions_root[child.index])
        )



    @Attribute
    def closed_solid(self):
        """ Return a solid version of this wing segment (thus without
        structural elements) with closed root and tip airfoils

        :rtype: parapy.geom.occ.sewing.CloseSurface
        """
        return CloseSurface([self.lower_surface, self.upper_surface])

    @Attribute
    def closed_shell(self):
        """ Return a outer shell version of this wing segment (thus without
        structural elements) with closed root and tip airfoils

        :rtype: parapy.geom.occ.shell.Shell_
        """
        return self.closed_solid.shells[0]

    @Attribute(in_tree=True)
    def avl_surface(self):
        """ Return the AVL Surface geometry. This representation is required
        the AVL wrapper.

        :rtype: parapy.lib.avl.primitives.Surface
        """
        sections = [self.root_airfoil.avl_section,
                    self.tip_airfoil.avl_section]

        return avl.Surface(name=self.name,
                           sections=sections,
                           n_chordwise=self.avl_n_chord,
                           n_spanwise=self.avl_n_span,
                           chord_spacing=self.avl_c_spacing,
                           span_spacing=self.avl_s_spacing)


if __name__ == '__main__':
    from parapy.gui import display
    from classes.wing_primitives.external.connecting_element import \
        ConnectingElement

    forward_wing = LiftingSurface(
        'NACA23012', 4., 1., 'whitcomb', 2., 4., 6., 35., 6.,
        n_spars=2,
        spar_chordwise_positions_root=[0.2, 0.8],
        spar_chordwise_positions_tip=[0.2, 0.8],
        spar_aspect_ratios=[0.2, 0.2], spar_profiles=['I', 'C'],
        spar_spanwise_positions_end=[0.8, 0.8],
        )

    vertical_wing = LiftingSurface(
        'NACA0012', 1.5, 0., 'NACA0012', 1., 0.,
        1.5, 45.,
        0., 0,
        position=rotate90(
            translate(
                forward_wing.tip_airfoil.position,
                forward_wing.leading_edge.direction_vector,
                forward_wing.tip_airfoil.max_thickness,
                forward_wing.orientation.Vx,
                forward_wing.tip_airfoil.chord - 1.5,
                forward_wing.orientation.Vz,
                forward_wing.tip_airfoil.max_thickness),
            'x'))

    connecting_element = ConnectingElement(forward_wing.tip_airfoil,
                                           vertical_wing.root_airfoil)
    # Display regular wing with winglet
    # display([forward_wing, vertical_wing, connecting_element])

    rear_wing = LiftingSurface(
        'NACA23012', 4., 1., 'whitcomb', 2., 4., 6., -35., -6.,
        n_spars=2,
        spar_chordwise_positions_root=[0.2, 0.8],
        spar_chordwise_positions_tip=[0.2, 0.8],
        spar_aspect_ratios=[0.2, 0.2], spar_profiles=['I', 'C'],
        spar_spanwise_positions_end=[0.8, 0.8],
        position=translate(forward_wing.position,
                           'x', 10.,
                           'z', 3.))

    bw_vertical = LiftingSurface(
        'NACA0012', 1.5, 0., 'NACA0012', 1., 0.,
        rear_wing.tip_airfoil.position.distance(
            forward_wing.tip_airfoil.position) -
        rear_wing.tip_airfoil.max_thickness -
        forward_wing.tip_airfoil.max_thickness - 0.35,
        degrees((rear_wing.position - forward_wing.position).angle(
            forward_wing.orientation.Vx)),
        0., 0,
        position=rotate90(
            translate(
                forward_wing.tip_airfoil.position,
                forward_wing.leading_edge.direction_vector,
                forward_wing.tip_airfoil.max_thickness,
                forward_wing.orientation.Vx,
                forward_wing.tip_airfoil.chord - 1.5,
                forward_wing.orientation.Vz,
                forward_wing.tip_airfoil.max_thickness),
            'x'
        ))

    display([forward_wing, bw_vertical, connecting_element, rear_wing])
