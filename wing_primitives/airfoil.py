import math
from os.path import join, dirname

import kbeutils.avl as avl
import numpy as np
import pandas as pd
import parapy.lib.xfoil as xfoil
from parapy.core import *
from parapy.geom import *
from parapy.lib.cst import CSTAirfoil

from tools.naca import *


class Airfoil(FittedCurve):
    # Q "Class Airfoil must implement all abstract methods" is shown as warning
    """ Returns an airfoil curve as a FittedCurve through the points as
    defined in the points method. Three airfoil kinds can be chosen.
    Firstly, one can supply a NACA 4- or 5-series airfoil name as 'NACAXXXX'
    or 'NACAXXXXX'. The airfoil input 'type' should be set to 'name' in this
    case.
    Secondly, one can supply a name of an airfoil .dat file,
    such as 'whitcomb', which will then be sought in the airfoil database
    directory. The airfoil input 'type' should be set to 'name' in this case.
    Finally, one can supply cst coefficients by filling in the
    corresponding cst_coefficients_u and cst_coefficients_l input slots. If
    this last method is chosen, the airfoil input 'type' should be set to
    'cst'.

    Optionally, one can supply a thickness factor (defaults to 1.) if one
    wants to adjust the thickness of the airfoil.

    Usage:
    Generating a NACA airfoil with chord 4:
    ::
        >>> my_naca2412_airfoil = Airfoil('NACA2412', 4)


    Generating a whitcomb airfoil with chord 4 from a .dat file:
    ::
        >>> my_dat_airfoil = Airfoil('whitcomb', 4)

    Generating a cst airfoil with chord 4 and 3 as well as 3 lower cst
    coefficients:
    ::
        >>> my_cst_airfoil = Airfoil(
        >>> chord=4, cst_coefficients_u = [0.3, 0.2, 0.1],
        >>> cst_coefficients_l= [-0.3, -0.2, 0], type='cst')
    """
    # Class constants
    CONSTANTS = pd.read_excel(
        join(dirname(dirname(__file__)), 'input', 'constants.xlsx'),
        sheet_name='aero', index_col=0
    )

    REYNOLDS = CONSTANTS.loc['reynolds']['value']
    REYNOLDS_UNITS = CONSTANTS.loc['reynolds']['units']
    MACH = CONSTANTS.loc['mach']['value']
    MACH_UNITS = CONSTANTS.loc['mach']['units']

    __initargs__ = ['airfoil_name', 'chord', 'twist', 'type',
                    'cst_coefficients_u', 'cst_coefficients_l',
                    'airfoil_number_of_points']

    # Required inputs if type == 'name'
    airfoil_name = Input(validator=val.is_string)
    chord = Input(validator=val.is_positive)
    twist = Input(validator=val.is_number)

    # Required inputs if type == 'cst'
    cst_coefficients_u = Input(validator=val.all_is_number)
    cst_coefficients_l = Input(validator=val.all_is_number)
    type = Input('name', validator=val.OneOf(['name', 'cst']))

    # Optional inputs
    thickness_factor = Input(1., validator=val.is_positive)
    airfoil_number_of_points = Input(100, validator=val.is_positive)
    name = Input('airfoil')
    alpha_start = Input(-15.)
    alpha_end = Input(15.)
    alpha_step = Input(1.)
    controls = Input([None])

    @Input
    def label(self):
        return self.name

    # Airfoil-specific methods and attributes.
    @Attribute
    def points(self):
        """ If the input "type" is "name", this attribute returns the
        coordinates of a NACA 4- or 5-series airfoil if the input airfoil_name
        is specified as NACAXXXX or NACAXXXXX, else it looks for a .dat file
        containing the airfoil name specified.
        If the input "type" is "cst", this attribute returns the coordinates of
        the airfoil corresponding to those CST coefficients, using the
        CSTAirfoil class, supplied by ParaPy.
        Coordinates run from trailing edge, over the upper surface, to the
        leading edge, towards the trailing edge again over the lower surface.

        :return: a list containing the airfoil coordinate points
        :rtype: list[parapy.geom.generic.positioning.Point]
        """
        airfoil_points = []

        if self.type == 'name' and self.airfoil_name.upper().startswith(
                'NACA'):
            # If NACA airfoil is supplied, run the NACA airfoil utility.
            number = self.airfoil_name.upper().replace('NACA', '')
            x_coor, z_coor = naca(number, self.airfoil_number_of_points)

            for x, z in zip(x_coor, z_coor):
                airfoil_points.append(
                    self.position.translate('x', self.chord * float(x),
                                            'z', self.chord * float(z) *
                                            self.thickness_factor)
                )

        elif self.type == 'name':
            # Else, try to open a dat file containing the supplied name.

            with open(join(dirname(dirname(__file__)), 'airfoils', '{}.dat'
                    .format(self.airfoil_name)),
                      'r') as f:
                for line in f.readlines():
                    x, z = line.strip('\n').split(' ')
                    airfoil_points.append(
                        self.position.translate('x', self.chord * float(x),
                                                'z', self.chord * float(z) *
                                                self.thickness_factor)
                    )

        else:
            # Transform axis system from XY to XZ and scale by chord
            airfoil_points = [self.position.translate('x', self.chord * pnt.x,
                                                      'z', self.chord * pnt.y *
                                                      self.thickness_factor)
                              for pnt in self.cst_airfoil.points]

        return airfoil_points

    @Attribute
    def orientation(self):
        """ The orientation of the airfoil is x in the streamwise direction,
        from leading edge to trailing edge. Z is taken as the upward
        direction (in the direction of the airfoil thickness). The y
        direction is then taken as the out-of-plane orthogonal vector.

        :rtype:
        """
        return Orientation(x=self.chord_line.direction_vector,
                           y=self.plane_normal if self.plane_normal.y > 0
                           else self.plane_normal.reverse)

    @Attribute
    def cst_airfoil(self):
        """ Returns the CST-based airfoil from the ParaPy-native CSTAirfoil
        class.

        :rtype: parapy.lib.cst.airfoil.CSTAirfoil
        """
        if self.type == 'cst':
            return CSTAirfoil(self.cst_coefficients_u,
                              self.cst_coefficients_l,
                              self.airfoil_number_of_points)
        else:
            return None

    @Attribute
    def trailing_edge_point(self):
        """ Return the rear-most point of the airfoil that defines the
        trailing edge (TE) point.

        :rtype: parapy.geom.generic.positioning.Point
        """
        return self.start

    @Attribute
    def leading_edge_point(self):
        """ Return the front-most point of the airfoil that defines the
        leading edge (LE) point.

        :rtype: parapy.geom.generic.positioning.Point
        """
        return self.extremum(self.trailing_edge_point, distance='max')['point']

    @Attribute
    def chord_line(self):
        """ Returns the line that defines the chord of the airfoil,
        from leading edge (LE) to trailing edge (TE).

        :rtype: parapy.geom.occ.curve.LineSegment
        """
        return LineSegment(self.leading_edge_point, self.trailing_edge_point)

    @Attribute
    def split_airfoil(self):
        """ Returns the airfoil curve as a curve split at the leading edge
        (LE) by the leading_edge_point.

        :rtype: parapy.geom.occ.wire.SplitCurve
        """
        return SplitCurve(self, self.leading_edge_point)

    @Attribute(in_tree=False)
    def upper_half(self):
        """ Returns the upper half of the airfoil curve split at the leading
        edge (LE) by the leading_edge_point. Finding the upper half is based
        on finding the half with its cog lying most upwards (+Z).

        :rtype: parapy.geom.occ.edge.Edge_
        """
        # Find the upper half of the airfoil by taking the airfoil with
        # the cog with the highest z-coordinate.
        airfoil_upper_half = max(self.split_airfoil.edges,
                                 key=lambda x: x.cog.z)
        # If the direction vector points in the positive x-dir:
        if airfoil_upper_half.direction_vector.x > 0:
            # Return the curve as is, because it respects sign convention.
            return airfoil_upper_half
        else:
            # Else, reverse the curve and then return.
            return airfoil_upper_half.reversed

    @Attribute(in_tree=False)
    def lower_half(self):
        """ Returns the upper half of the airfoil curve split at the leading
        edge (LE) by the leading_edge_point. Finding the lower half is based
        on finding the half with its cog lying most downwards (-Z).

        :rtype: parapy.geom.occ.edge.Edge_
        """
        # Find the lower half of the airfoil by taking the airfoil with
        # the cog with the lowest z-coordinate.
        airfoil_lower_half = min(self.split_airfoil.edges,
                                 key=lambda x: x.cog.z)
        # If the direction vector points in the positive x-dir:
        if airfoil_lower_half.direction_vector.x > 0:
            # Return the curve as is, because it respects sign convention.
            return airfoil_lower_half
        else:
            # Else, reverse the curve and then return.
            return airfoil_lower_half.reversed

    @Attribute(settable=False)
    def max_thickness(self):
        """ Return the maximum thickness of the airfoil.

        :rtype: float
        """
        return max([self.upper_half.point(u).distance(self.lower_half.point(u))
                    for u in np.arange(0, 1, 1e-3)])

    @Attribute
    def plane(self):
        """ Returns the plane that contains this airfoil.

        :rtype: parapy.geom.occ.surface.Plane
        """
        return Plane(self.position, self.plane_normal, self.orientation.Vx)

    @Attribute
    def cog(self):
        return Wire([self.upper_half, self.lower_half]).cog

    @Attribute
    def camber_points(self):
        """ Returns the points that define the camber line, lying halfway
        between the upper and lower airfoil lines.

        :rtype: list[parapy.geom.generic.positioning.Point]
        """
        n_points = self.airfoil_number_of_points

        points_u = self.upper_half.equispaced_points(n_points)
        points_l = self.lower_half.equispaced_points(n_points)

        return [x_u.midpoint(x_l) for x_u, x_l in zip(points_u, points_l)]

    @Attribute
    def camber_line(self):
        """ Return the camber line as a curve fitted through the camber points.

        :rtype: parapy.geom.occ.curve.FittedCurve
        """
        return FittedCurve(self.camber_points)

    @Attribute
    def coordinates(self):
        return self.points

    @Attribute
    def avl_section(self):
        """ Returns the AVL-compatible airfoil section representation of
        this airfoil.

        :rtype: parapy.lib.avl.primitives.AirfoilCurveSection
        """
        airfoil = avl.DataAirfoil.from_airfoil_curve(self)
        return avl.Section(
            chord=self.chord,
            airfoil=airfoil,
            position=self.position,
            controls=self.controls
        )

    @Attribute
    def xfoil_results(self):
        """ Runs an xfoil analysis for this airfoil. If the airfoil is an
        :any:`IntersectedAirfoil`, the points are rotated by its twist angle
        first, such that the airfoil's geometry input to xfoil corresponds
        to its actual angle of attack.

        :rtype: list[dict[str, float]]
        """
        keys = ['alpha', 'CL', 'CD', 'CDp', 'CM', 'Top_Xtr', 'Bot_Xt']
        alpha = (self.alpha_start, self.alpha_end, self.alpha_step)
        airfoil_in_plane = xfoil.points_in_plane(self.points, Point(0, 0, 0),
                                                 Vector(0, 1, 0),
                                                 Vector(1, 0, 0))

        if isinstance(self, IntersectedAirfoil):
            leading_edge = min(airfoil_in_plane, key=lambda p: p.x)
            airfoil_in_plane = [rotate(point,
                                       self.surface.position.Vz,
                                       self.twist,
                                       ref=leading_edge,
                                       deg=True)
                                for point in airfoil_in_plane]

        results = xfoil.run_xfoil(
            airfoil_in_plane, self.REYNOLDS, alpha, self.MACH,
            norm=True, pane=True, cleanup=True
        )
        return [{key: value for key, value in zip(keys, result)}
                for result in results]

    @Attribute
    def CM_0(self):
        """ Returns the airfoil's zero-angle-of-attack pitching moment
        coefficient. If no zero-AoA XFOIL analysis has been run, it takes
        the picthing moment coefficient of the run with the AoA nearest to
        zero.

        :rtype: float
        """
        return min(self.xfoil_results, key=lambda dct: dct['alpha'])['CM']

    @Attribute
    def CL_0(self):
        """ Returns the airfoil's zero-angle-of-attack lift coefficient.
        Assumes a linear variation of the lift coefficient with angle of
        attack. Only uses the linear range of the airfoil (AoA = [-8, 8]).

        :rtype: float
        """
        alpha_min = -8
        alpha_max = 8
        alphas = [result['alpha'] for result in self.xfoil_results
                  if alpha_min <= result['alpha'] <= alpha_max]
        CLs = [result['CL'] for result in self.xfoil_results
               if alpha_min <= result['alpha'] <= alpha_max]
        return np.polyfit(alphas, CLs, 1)[-1]

    @Attribute
    def CL_alpha(self):
        """ Returns the airfoil's lift coefficient gradient in deg\ :sup:`-1`\
        .
        Assumes a linear variation of the lift coefficient with angle of
        attack. Only uses the linear range of the airfoil (AoA = [-8, 8]).

        :rtype: float
        """
        alpha_min = -8
        alpha_max = 8
        alphas = [result['alpha'] for result in self.xfoil_results
                  if alpha_min <= result['alpha'] <= alpha_max]
        CLs = [result['CL'] for result in self.xfoil_results
               if alpha_min <= result['alpha'] <= alpha_max]
        return np.polyfit(alphas, CLs, 1)[0]


class IntersectedAirfoil(Airfoil):
    """ Returns an airfoil :any:`Airfoil` as an intersection between a lifting
    :any:`surface` and a :any:`plane`.
    """
    plane = Input()
    surface = Input()

    __initargs__ = ['surface', 'plane']

    @Attribute
    def position(self):
        return Position(self.leading_edge_point,
                        Orientation(x=self.chord_line.direction_vector,
                                    y=self.plane_normal))

    @Attribute
    def intersection_curve(self):
        return Wire(IntersectedShapes(self.surface, self.plane).edges)

    @Attribute
    def points(self):
        f = self.intersection_curve.point
        leading_edge = max(self.intersection_curve
                           .point_extrema(self.intersection_curve.start),
                           key=lambda dct: dct['distance'])
        u_leading_edge = leading_edge['u']
        n_half = self.airfoil_number_of_points // 2 + 1
        lst1 = [f(u) for u in xfoil.main.sine_distribution(
            n_half, self.intersection_curve.u1, u_leading_edge,
            theta1=0., theta2=math.pi / 2)]

        lst2 = [f(u) for u in xfoil.main.cosine_distribution(
            n_half, u_leading_edge, self.intersection_curve.u2,
            theta1=0, theta2=math.pi / 2)]
        return lst1 + lst2[1:]

    @Attribute
    def chord(self):
        return self.chord_line.length

    @Attribute
    def twist(self):
        chord_dir = self.chord_line.direction_vector
        is_negative = chord_dir.z > self.surface.orientation.Vx.z
        angle = self.surface.position.Vx.angle(chord_dir, deg=True)
        return -angle if is_negative else angle


if __name__ == '__main__':
    from parapy.gui import display

    obj = Airfoil('NACA23012',
                  4.,
                  name='airfoil')
    display(obj)
